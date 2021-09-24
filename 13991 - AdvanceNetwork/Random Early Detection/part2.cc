/** Network topology
 *
 *    100Mb/s, 1ms  
 * n0---------------|
 *                  |   1.5Mbps/s, 20ms        45Mb/s, 20ms
 *                  n2-------------------n3-------------------n4
 *    100Mb/s, 1ms  | <---- Gateway ---->
 * n1---------------|
 *
 */

#include "ns3/core-module.h"
#include "ns3/network-module.h"
#include "ns3/internet-module.h"
#include "ns3/flow-monitor-helper.h"
#include "ns3/point-to-point-module.h"
#include "ns3/applications-module.h"
#include "ns3/traffic-control-module.h"

using namespace ns3;

uint32_t checkTimes;
double avgQueueSize;

std::stringstream filePlotQueue;
std::stringstream filePlotQueueAvg;

void
CheckQueueSize (Ptr<QueueDisc> queue)
{
  uint32_t qSize = queue->GetCurrentSize ().GetValue ();

  avgQueueSize += qSize;
  checkTimes++;

  // check queue size every 1/100 of a second
  Simulator::Schedule (Seconds (0.01), &CheckQueueSize, queue);

  std::ofstream fPlotQueue (filePlotQueue.str ().c_str (), std::ios::out|std::ios::app);
  fPlotQueue << Simulator::Now ().GetSeconds () << " " << qSize << std::endl;
  fPlotQueue.close ();

  std::ofstream fPlotQueueAvg (filePlotQueueAvg.str ().c_str (), std::ios::out|std::ios::app);
  fPlotQueueAvg << Simulator::Now ().GetSeconds () << " " << avgQueueSize / checkTimes << std::endl;
  fPlotQueueAvg.close ();
}

int
main (int argc, char *argv[])
{

  std::string redLinkDataRate = "1.5Mbps"; // Assumption
  std::string redLinkDelay = "20ms"; // Assumption

  uint32_t simDuration = 10.0;
  std::string pathOut = "./results/part2";
  bool writeForPlot = true;
  bool writePcap = true;
  bool flowMonitor = false;
  bool printRedStats = true;

  // Configuration and command line parameter parsing
  // Will only save in the directory if enable opts below
  CommandLine cmd (__FILE__);
  cmd.AddValue ("simDuration", "Simulation duration", simDuration);
  cmd.AddValue ("pathOut", "Path to save results from --writeForPlot/--writePcap/--writeFlowMonitor", pathOut);
  cmd.AddValue ("writeForPlot", "<0/1> to write results for plot (gnuplot)", writeForPlot);
  cmd.AddValue ("writePcap", "<0/1> to write results in pcapfile", writePcap);
  cmd.AddValue ("writeFlowMonitor", "<0/1> to enable Flow Monitor and write their results", flowMonitor);

  cmd.Parse (argc, argv);

  SeedManager::SetSeed(1);
  SeedManager::SetRun (0);
  Time::SetResolution (Time::NS);

  // Create nodes
  NodeContainer nodes;
  nodes.Create (5);

  Config::SetDefault ("ns3::TcpL4Protocol::SocketType", StringValue ("ns3::TcpNewReno"));
  // 42 = headers size
  Config::SetDefault ("ns3::TcpSocket::SegmentSize", UintegerValue (1000 - 42));
  Config::SetDefault ("ns3::TcpSocket::DelAckCount", UintegerValue (1));
  GlobalValue::Bind ("ChecksumEnabled", BooleanValue (false));

  uint32_t meanPktSize = 500;

  // RED params
  Config::SetDefault ("ns3::RedQueueDisc::MaxSize", StringValue ("1000p"));
  Config::SetDefault ("ns3::RedQueueDisc::MeanPktSize", UintegerValue (meanPktSize));
  Config::SetDefault ("ns3::RedQueueDisc::Wait", BooleanValue (true));
  Config::SetDefault ("ns3::RedQueueDisc::Gentle", BooleanValue (true));
  Config::SetDefault ("ns3::RedQueueDisc::LInterm", DoubleValue (0.02));
  Config::SetDefault ("ns3::RedQueueDisc::QW", DoubleValue (0.002));
  Config::SetDefault ("ns3::RedQueueDisc::MinTh", DoubleValue (5));
  Config::SetDefault ("ns3::RedQueueDisc::MaxTh", DoubleValue (15));

  // Install internet stack on all nodes
  InternetStackHelper internet;
  internet.Install (nodes);

  TrafficControlHelper tchPfifo;
  uint16_t handle = tchPfifo.SetRootQueueDisc ("ns3::PfifoFastQueueDisc");
  tchPfifo.AddInternalQueues (handle, 3, "ns3::DropTailQueue", "MaxSize", StringValue ("1000p"));

  TrafficControlHelper tchRed;
  tchRed.SetRootQueueDisc ("ns3::RedQueueDisc", "LinkBandwidth", StringValue (redLinkDataRate),
                           "LinkDelay", StringValue (redLinkDelay));

  // Create channels
  PointToPointHelper p2p;

  p2p.SetQueue ("ns3::DropTailQueue");
  p2p.SetDeviceAttribute ("DataRate", StringValue ("100Mbps"));
  p2p.SetChannelAttribute ("Delay", StringValue ("1ms"));
  NetDeviceContainer devn0n2 = p2p.Install (nodes.Get(0), nodes.Get(2));
  tchPfifo.Install (devn0n2);

  NetDeviceContainer devn1n2 = p2p.Install (nodes.Get(1), nodes.Get(2));
  tchPfifo.Install (devn1n2);

  p2p.SetDeviceAttribute ("DataRate", StringValue ("45Mbps"));
  p2p.SetChannelAttribute ("Delay", StringValue ("20ms"));
  NetDeviceContainer devn3n4 = p2p.Install (nodes.Get(3), nodes.Get(4));
  tchPfifo.Install (devn3n4);

  p2p.SetQueue ("ns3::DropTailQueue");
  p2p.SetDeviceAttribute ("DataRate", StringValue (redLinkDataRate));
  p2p.SetChannelAttribute ("Delay", StringValue (redLinkDelay));
  NetDeviceContainer devn2n3 = p2p.Install (nodes.Get(2), nodes.Get(3));
  // only backbone link has RED queue disc
  QueueDiscContainer queueDiscs = tchRed.Install (devn2n3);

  // Assign IP Addresses
  Ipv4AddressHelper ipv4;

  ipv4.SetBase ("10.1.0.0", "255.255.255.0");
  Ipv4InterfaceContainer i0i2 = ipv4.Assign (devn0n2);

  ipv4.SetBase ("10.1.1.0", "255.255.255.0");
  Ipv4InterfaceContainer i1i2 = ipv4.Assign (devn1n2);

  ipv4.SetBase ("10.1.2.0", "255.255.255.0");
  Ipv4InterfaceContainer i2i3 = ipv4.Assign (devn2n3);

  ipv4.SetBase ("10.1.3.0", "255.255.255.0");
  Ipv4InterfaceContainer i3i4 = ipv4.Assign (devn3n4);

  // Set up the routing
  Ipv4GlobalRoutingHelper::PopulateRoutingTables ();

  // Create applications
  // SINK is installed on n4
  uint16_t port = 50000;
  Address sinkLocalAddress (InetSocketAddress (Ipv4Address::GetAny (), port));
  PacketSinkHelper sinkHelper ("ns3::TcpSocketFactory", sinkLocalAddress);
  ApplicationContainer sinkApp = sinkHelper.Install (nodes.Get(4));

  // Sender is installed on n0, n1
  ApplicationContainer sendApp;
  BulkSendHelper bulkSend ("ns3::TcpSocketFactory", Address ());
  AddressValue remoteAddress
    (InetSocketAddress (i3i4.GetAddress (1), port));
  bulkSend.SetAttribute ("Remote", remoteAddress);
  sendApp = bulkSend.Install (nodes.Get(0));
  sendApp.Start (Seconds (0.0));
  sendApp = bulkSend.Install (nodes.Get(1));
  sendApp.Start (Seconds (0.2));

  if (writePcap)
    {
      PointToPointHelper ptp;
      std::stringstream stmp;
      stmp << pathOut << "/red";
      ptp.EnablePcapAll (stmp.str ().c_str ());
    }

  Ptr<FlowMonitor> flowmon;
  if (flowMonitor)
    {
      FlowMonitorHelper flowmonHelper;
      flowmon = flowmonHelper.InstallAll ();
    }

  if (writeForPlot)
    {
      filePlotQueue << pathOut << "/" << "red-queue.plotme";
      filePlotQueueAvg << pathOut << "/" << "red-queue_avg.plotme";

      remove (filePlotQueue.str ().c_str ());
      remove (filePlotQueueAvg.str ().c_str ());
      Ptr<QueueDisc> queue = queueDiscs.Get (0);
      Simulator::ScheduleNow (&CheckQueueSize, queue);
    }

  Simulator::Stop (Seconds (simDuration));
  Simulator::Run ();

  if (flowMonitor)
    {
      std::stringstream stmp;
      stmp << pathOut << "/red.flowmon";

      flowmon->SerializeToXmlFile (stmp.str ().c_str (), false, false);
    }

  if (printRedStats)
    {
      QueueDisc::Stats st = queueDiscs.Get (0)->GetStats ();
      std::cout << "*** RED stats from Node 2 queue disc ***" << std::endl;
      std::cout << st << std::endl;

      st = queueDiscs.Get (1)->GetStats ();
      std::cout << "*** RED stats from Node 3 queue disc ***" << std::endl;
      std::cout << st << std::endl;
    }

  Simulator::Destroy ();

  return 0;
}
