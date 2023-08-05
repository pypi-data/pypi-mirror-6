
import clusto
from clusto.test import testbase

from clusto.drivers import IPManager, BasicServer, ResourceTypeException, ResourceException

import IPy

class IPManagerTest(testbase.ClustoTestBase):

    def data(self):

        ip1 = IPManager('a1', gateway='192.168.1.1', netmask='255.255.255.0',
                        baseip='192.168.1.0')

        ip2 = IPManager('b1', gateway='10.0.128.1', netmask='255.255.252.0',
                        baseip='10.0.128.0')

        ip3 = IPManager('c1', gateway='172.16.40.0', netmask='255.255.255.0',
                        baseip='172.16.40.0')
        
        ip4 = IPManager('c2', gateway='172.16.0.0', netmask='255.255.0.0',
                        baseip='172.16.0.0')

        s = BasicServer('s1')

    def testBadIPAllocation(self):
        
        ip1, ip2, s1 = map(clusto.get_by_name, ['a1', 'b1', 's1'])

        self.assertRaises(ResourceTypeException, ip1.allocate, s1, '10.2.3.4')

    def testNewIP(self):
        
        ip1, ip2, s1 = map(clusto.get_by_name, ['a1', 'b1', 's1'])

        num = 50
        for i in range(num):
            ip1.allocate(s1)


        self.assertEqual(ip1.count, num)
        self.assertEqual(len(ip1.resources(s1)), num)
        
        self.assertEqual(ip1.owners('192.168.1.' + str(num+1)), [s1])

    def testGetIPManager(self):

        ip1, ip2 = map(clusto.get_by_name, ['a1', 'b1'])

        self.assertEqual(ip1, IPManager.get_ip_manager('192.168.1.23'))
        self.assertEqual(ip2, IPManager.get_ip_manager('10.0.129.22'))

    def testGetIPManagers(self):
        ip3, ip4 = map(clusto.get_by_name, ['c1', 'c2'])

        self.assertEqual([ip3, ip4], IPManager.get_ip_managers('172.16.40.2'))
        self.assertEqual([ip4], IPManager.get_ip_managers('172.16.0.2'))
        self.assertEqual([], IPManager.get_ip_managers('192.168.40.1'))

    def testGetIP(self):

        ip1, ip2, s1 = map(clusto.get_by_name, ['a1', 'b1', 's1'])

        ip1.allocate(s1)
        ip2.allocate(s1)

        self.assertEqual(sorted(IPManager.get_ips(s1)),
                         sorted(['192.168.1.2', '10.0.128.2']))

    def testReserveIP(self):
        
        ip1, ip2, s1 = map(clusto.get_by_name, ['a1', 'b1', 's1'])

        ip2.allocate(ip2, '10.0.128.4')

        self.assertRaises(ResourceException, ip2.allocate, s1, '10.0.128.4')

        
