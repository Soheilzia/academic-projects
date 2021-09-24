/** Network topology
 *
 *    100Mb/s, 0.5ms                                                                  100Mb/s, 0.5ms
 * n0---------------|                                                               |---------------n8
 *                  |                                                               |
 *                  |                                                               |
 *    100Mb/s, 1ms  |                                                               | 100Mb/s, 1ms
 * n1---------------|                                                               |---------------n9
 *                  |   1.5Mbps/s, 20ms        45Mb/s, 2ms       1.5Mbps/s, 20ms    |
 *                  n4-------------------n5-------------------n6-------------------n7
 *    100Mb/s, 3ms  | <--- Gateway A ---->                     <--- Gateway B ----> | 100Mb/s, 5ms
 * n2---------------|                                                               |---------------n10
 *                  |                                                               |
 *                  |                                                               |
 *    100Mb/s, 5ms  |                                                               | 100Mb/s, 2ms
 * n3---------------|                                                               |---------------n11
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
double avgQueueSizeA;
double avgQueueSizeB;

std::stringstream filePlotQueueA;
std::stringstream filePlotQueueAAvg;

std::stringstream filePlotQueueB;
std::stringstream filePlotQueueBAvg;

void
CheckQueueSize (Ptr<QueueDisc> queueA, Ptr<QueueDisc> queueB)
{
  uint32_t qSizeA = queueA->GetCurrentSize ().GetValue ();
  uint32_t qSizeB = queueB->GetCurrentSize ().GetValue ();

  avgQueueSizeA += qSizeA;
  avgQueueSizeB += qSizeB;
  checkTimes++;

  // check queue size every 1/100 of a second
  Simulator::Schedule (Seconds (0.01), &CheckQueueSize, queueA, queueB);

  std::ofstream fPlotQueueA (filePlotQueueA.str ().c_str (), std::ios::out|std::ios::app);
  fPlotQueueA << Simulator::Now ().GetSeconds () << " " << qSizeA << std::endl;
  fPlotQueueA.close ();

  std::ofstream fPlotQueueAAvg (filePlotQueueAAvg.str ().c_str (), std::ios::out|std::ios::app);
  fPlotQueueAAvg << Simulator::Now ().GetSeconds () << " " << avgQueueSizeA / checkTimes << std::endl;
  fPlotQueueAAvg.close ();

  std::ofstream fPlotQueueB (filePlotQueueB.str ().c_str (), std::ios::out|std::ios::app);
  fPlotQueueB << Simulator::Now ().GetSeconds () << " " << qSizeB << std::endl;
  fPlotQueueB.close ();

  std::ofstream fPlotQueueBAvg (filePlotQueueBAvg.str ().c_str (), std::ios::out|std::ios::app);
  fPlotQueueBAvg << Simulator::Now ().GetSeconds () << " " << avgQueueSizeB / checkTimes << std::endl;
  fPlotQueueBAvg.close ();
}

int
main (int argc, char *argv[])
{

  std::string redLinkDataRate = "1.5Mbps"; // Assumption
  std::string redLinkDelay = "20ms"; // Assumption

  uint32_t simDuration = 10.0;
  std::string pathOut = "./results/part3";
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
  nodes.Create (12);

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
  p2p.SetChannelAttribute ("Delay", StringValue ("0.5ms"));
  NetDeviceContainer devn0n4 = p2p.Install (nodes.Get(0), nodes.Get(4));
  tchPfifo.Install (devn0n4);

  p2p.SetChannelAttribute ("Delay", StringValue ("1ms"));
  NetDeviceContainer devn1n4 = p2p.Install (nodes.Get(1), nodes.Get(4));
  tchPfifo.Install (devn1n4);

  p2p.SetChannelAttribute ("Delay", StringValue ("3ms"));
  NetDeviceContainer devn2n4 = p2p.Install (nodes.Get(2), nodes.Get(4));
  tchPfifo.Install (devn2n4);

  p2p.SetChannelAttribute ("Delay", StringValue ("5ms"));
  NetDeviceContainer devn3n4 = p2p.Install (nodes.Get(3), nodes.Get(4));
  tchPfifo.Install (devn3n4);

  p2p.SetChannelAttribute ("Delay", StringValue ("0.5ms"));
  NetDeviceContainer devn7n8 = p2p.Install (nodes.Get(7), nodes.Get(8));
  tchPfifo.Install (devn7n8);

  p2p.SetChannelAttribute ("Delay", StringValue ("1ms"));
  NetDeviceContainer devn7n9 = p2p.Install (nodes.Get(7), nodes.Get(9));
  tchPfifo.Install (devn7n9);

  p2p.SetChannelAttribute ("Delay", StringValue ("5ms"));
  NetDeviceContainer devn7n10 = p2p.Install (nodes.Get(7), nodes.Get(10));
  tchPfifo.Install (devn7n10);

  p2p.SetChannelAttribute ("Delay", StringValue ("2ms"));
  NetDeviceContainer devn7n11 = p2p.Install (nodes.Get(7), nodes.Get(11));
  tchPfifo.Install (devn7n11);

  p2p.SetDeviceAttribute ("DataRate", StringValue ("45Mbps"));
  p2p.SetChannelAttribute ("Delay", StringValue ("2ms"));
  NetDeviceContainer devn5n6 = p2p.Install (nodes.Get(5), nodes.Get(6));
  tchPfifo.Install (devn5n6);

  p2p.SetQueue ("ns3::DropTailQueue");
  p2p.SetDeviceAttribute ("DataRate", StringValue (redLinkDataRate));
  p2p.SetChannelAttribute ("Delay", StringValue (redLinkDelay));
  NetDeviceContainer devn4n5 = p2p.Install (nodes.Get(4), nodes.Get(5));
  NetDeviceContainer devn6n7 = p2p.Install (nodes.Get(6), nodes.Get(7));
  // only backbone link has RED queue disc
  QueueDiscContainer queueDiscsA = tchRed.Install (devn4n5);
  QueueDiscContainer queueDiscsB = tchRed.Install (devn6n7);

  // Assign IP Addresses
  Ipv4AddressHelper ipv4;

  ipv4.SetBase ("10.1.0.0", "255.255.255.0");
  Ipv4InterfaceContainer i0i4 = ipv4.Assign (devn0n4);

  ipv4.SetBase ("10.1.1.0", "255.255.255.0");
  Ipv4InterfaceContainer i1i4 = ipv4.Assign (devn1n4);

  ipv4.SetBase ("10.1.2.0", "255.255.255.0");
  Ipv4InterfaceContainer i2i4 = ipv4.Assign (devn2n4);

  ipv4.SetBase ("10.1.3.0", "255.255.255.0");
  Ipv4InterfaceContainer i3i4 = ipv4.Assign (devn3n4);

  ipv4.SetBase ("10.1.4.0", "255.255.255.0");
  Ipv4InterfaceContainer i4i5 = ipv4.Assign (devn4n5);

  ipv4.SetBase ("10.1.5.0", "255.255.255.0");
  Ipv4InterfaceContainer i5i6 = ipv4.Assign (devn5n6);

  ipv4.SetBase ("10.1.6.0", "255.255.255.0");
  Ipv4InterfaceContainer i6i7 = ipv4.Assign (devn6n7);

  ipv4.SetBase ("10.1.7.0", "255.255.255.0");
  Ipv4InterfaceContainer i7i8 = ipv4.Assign (devn7n8);

  ipv4.SetBase ("10.1.8.0", "255.255.255.0");
  Ipv4InterfaceContainer i7i9 = ipv4.Assign (devn7n9);

  ipv4.SetBase ("10.1.9.0", "255.255.255.0");
  Ipv4InterfaceContainer i7i10 = ipv4.Assign (devn7n10);

  ipv4.SetBase ("10.1.10.0", "255.255.255.0");
  Ipv4InterfaceContainer i7i11 = ipv4.Assign (devn7n11);

  // Set up the routing
  Ipv4GlobalRoutingHelper::PopulateRoutingTables ();

  // Create applications
  // SINK is installed on n0, n1, n2, n3, n8, n9, n10, n11
  uint16_t port = 50000;
  ApplicationContainer sinkApp;
  Address sinkLocalAddress (InetSocketAddress (Ipv4Address::GetAny (), port));
  PacketSinkHelper sinkHelper ("ns3::TcpSocketFactory", sinkLocalAddress);
  sinkApp = sinkHelper.Install (nodes.Get(0));
  sinkApp = sinkHelper.Install (nodes.Get(1));
  sinkApp = sinkHelper.Install (nodes.Get(2));
  sinkApp = sinkHelper.Install (nodes.Get(3));
  sinkApp = sinkHelper.Install (nodes.Get(8));
  sinkApp = sinkHelper.Install (nodes.Get(9));
  sinkApp = sinkHelper.Install (nodes.Get(10));
  sinkApp = sinkHelper.Install (nodes.Get(11));

  // Sender is installed on n0, n1, n2, n3, n8, n9, n10, n11
  ApplicationContainer sendApp;
  BulkSendHelper bulkSend ("ns3::TcpSocketFactory", Address ());
  AddressValue remoteAddress
    (InetSocketAddress (i7i8.GetAddress (1), port));
  bulkSend.SetAttribute ("Remote", remoteAddress);
  sendApp = bulkSend.Install (nodes.Get(0));
  remoteAddress = AddressValue (InetSocketAddress (i7i9.GetAddress (1), port));
  bulkSend.SetAttribute ("Remote", remoteAddress);
  sendApp = bulkSend.Install (nodes.Get(1));
  remoteAddress = AddressValue (InetSocketAddress (i7i10.GetAddress (1), port));
  bulkSend.SetAttribute ("Remote", remoteAddress);
  sendApp = bulkSend.Install (nodes.Get(2));
  remoteAddress = AddressValue (InetSocketAddress (i7i11.GetAddress (1), port));
  bulkSend.SetAttribute ("Remote", remoteAddress);
  sendApp = bulkSend.Install (nodes.Get(3));
  remoteAddress = AddressValue (InetSocketAddress (i0i4.GetAddress (0), port));
  bulkSend.SetAttribute ("Remote", remoteAddress);
  sendApp = bulkSend.Install (nodes.Get(8));
  remoteAddress = AddressValue (InetSocketAddress (i1i4.GetAddress (0), port));
  bulkSend.SetAttribute ("Remote", remoteAddress);
  sendApp = bulkSend.Install (nodes.Get(9));
  remoteAddress = AddressValue (InetSocketAddress (i2i4.GetAddress (0), port));
  bulkSend.SetAttribute ("Remote", remoteAddress);
  sendApp = bulkSend.Install (nodes.Get(10));
  remoteAddress = AddressValue (InetSocketAddress (i3i4.GetAddress (0), port));
  bulkSend.SetAttribute ("Remote", remoteAddress);
  sendApp = bulkSend.Install (nodes.Get(11));

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
      filePlotQueueA << pathOut << "/" << "red-queue-A.plotme";
      filePlotQueueAAvg << pathOut << "/" << "red-queue-A_avg.plotme";

      remove (filePlotQueueA.str ().c_str ());
      remove (filePlotQueueAAvg.str ().c_str ());
      Ptr<QueueDisc> queueA = queueDiscsA.Get (0);

      filePlotQueueB << pathOut << "/" << "red-queue-B.plotme";
      filePlotQueueBAvg << pathOut << "/" << "red-queue-B_avg.plotme";

      remove (filePlotQueueB.str ().c_str ());
      remove (filePlotQueueBAvg.str ().c_str ());
      Ptr<QueueDisc> queueB = queueDiscsB.Get (1);

      Simulator::ScheduleNow (&CheckQueueSize, queueA, queueB);
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
      QueueDisc::Stats st = queueDiscsA.Get (0)->GetStats ();
      std::cout << "*** RED stats from Node 4 queue disc ***" << std::endl;
      std::cout << st << std::endl;

      st = queueDiscsA.Get (1)->GetStats ();
      std::cout << "*** RED stats from Node 5 queue disc ***" << std::endl;
      std::cout << st << std::endl;

      st = queueDiscsB.Get (0)->GetStats ();
      std::cout << "*** RED stats from Node 6 queue disc ***" << std::endl;
      std::cout << st << std::endl;

      st = queueDiscsB.Get (1)->GetStats ();
      std::cout << "*** RED stats from Node 7 queue disc ***" << std::endl;
      std::cout << st << std::endl;
    }

  Simulator::Destroy ();

  return 0;
}
