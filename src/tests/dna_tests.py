'''
Created on 24 Jun 2012

@author: Qasim
'''

import sys
import os.path
sys.path[0] = os.path.dirname(sys.path[0])

import unittest
import dna

class BaseBuildTests(unittest.TestCase):
    def test_creation_from_string(self):
        """Test creating from a single string which contains only a base build"""
        s = "bu1"
        exres = dna.BaseBuild(dna.Tower.blue, dna.TowerLocation.l1)
        self.assertEqual(dna.BaseBuild.from_string(s), exres)
        
        s = "bw20"
        exres = dna.BaseBuild(dna.Tower.yellow, dna.TowerLocation.l20)
        self.assertEqual(dna.BaseBuild.from_string(s), exres)
        
        s = "uu5"
        with self.assertRaises(dna.BaseBuildInvalidStringError) as cm:
            dna.BaseBuild.from_string(s)
        cme = cm.exception
        self.assertEqual(cme.s, s)
        self.assertEqual(cme.location, 0)
        
        s = "ba6"
        with self.assertRaises(dna.BaseBuildInvalidStringError) as cm:
            dna.BaseBuild.from_string(s)
        cme = cm.exception
        self.assertEqual(cme.s, s)
        self.assertEqual(cme.location, 1)

        s = "bu0"
        with self.assertRaises(dna.BaseBuildInvalidStringError) as cm:
            dna.BaseBuild.from_string(s)
        cme = cm.exception
        self.assertEqual(cme.s, s)
        self.assertEqual(cme.location, 2)

        s = "bu6a"
        with self.assertRaises(dna.BaseBuildInvalidStringError) as cm:
            dna.BaseBuild.from_string(s)
        cme = cm.exception
        self.assertEqual(cme.s, s)
        self.assertEqual(cme.location, 2)
    
    def test_creation_from_string_info(self):
        s = "bu17u8"
        exres = dna.BaseBuild(dna.Tower.blue, dna.TowerLocation.l17), 4
        self.assertEqual(dna.BaseBuild.from_string_info(s), exres)
    
    def test_to_string(self):
        out = str(dna.BaseBuild(dna.Tower.yellow, dna.TowerLocation.l8))
        exres = "bw8"
        self.assertEqual(out, exres)
    
        out = str(dna.BaseBuild(dna.Tower.green, dna.TowerLocation.l20))
        exres = "bv20"
        self.assertEqual(out, exres)


class BaseUpgradeTests(unittest.TestCase):
    def test_creation_from_string(self):
        s = "u8"
        exres = dna.BaseUpgrade(dna.TowerLocation.l8)
        self.assertEqual(dna.BaseUpgrade.from_string(s), exres)
        
        s = "u0"
        with self.assertRaises(dna.BaseUpgradeInvalidStringError) as cm:
            dna.BaseUpgrade.from_string(s)
        cme = cm.exception
        self.assertEqual(cme.s, s)
    
    def test_creation_from_string_info(self):
        s = "u14bu8"
        exres = dna.BaseUpgrade(dna.TowerLocation.l14), 3
        self.assertEqual(dna.BaseUpgrade.from_string_info(s), exres)
    
    def test_to_string(self):
        out = str(dna.BaseUpgrade(dna.TowerLocation.l4))
        exres = "u4"
        self.assertEqual(out, exres)


class DNATests(unittest.TestCase):
    def test_creation_from_string_success(self):
        s = "bu1bv12bw9u1u12u9"
        d = dna.DNA.from_string(s)
        
        self.assertEqual(d[0], dna.BaseBuild("u", 1))
        self.assertEqual(d[1], dna.BaseBuild("v", 12))
        self.assertEqual(d[2], dna.BaseBuild("w", 9))
        self.assertEqual(d[3], dna.BaseUpgrade(1))
        self.assertEqual(d[4], dna.BaseUpgrade(12))
        self.assertEqual(d[5], dna.BaseUpgrade(9))
        self.assertEqual(len(d), 6)
    
    def test_creation_from_string_failure(self):
        #Invalid tower type in string
        s = "bu1ba2"
        the_dna = dna.DNA()
        with self.assertRaises(dna.DNAInvalidCreationString) as cm:
            the_dna.from_string(s)
        cme = cm.exception
        self.assertEqual(cme.loc, 3)
        
        #Invalid location to upgrade in string
        s = "bu1u1bu0"
        the_dna = dna.DNA()
        with self.assertRaises(dna.DNAInvalidCreationString) as cm:
            the_dna.from_string(s)
        cme = cm.exception
        self.assertEqual(cme.loc, 5)
        
        #General invalid string
        s = "abcdefg"
        the_dna = dna.DNA()
        with self.assertRaises(dna.DNAInvalidCreationString) as cm:
            the_dna.from_string(s)
        cme = cm.exception
        self.assertEqual(cme.loc, 0)
    
    def test_to_string(self):
        s = "bu1bv2bw9u1u2u9bu3"
        d = dna.DNA(s)
        self.assertEqual(str(d), s)
    
    def test_traverse(self):
        d = dna.DNA("bu1bu12bv3")
        
        g = d.__iter__()
        self.assertEqual(dna.BaseBuild(dna.Tower.blue, 1), next(g))
        self.assertEqual(dna.BaseBuild(dna.Tower.blue, 12), next(g))
        self.assertEqual(dna.BaseBuild(dna.Tower.green, 3), next(g))
        self.assertRaises(StopIteration, next, g)
    
    def test_validation_list_success(self):
        lst = [dna.BaseBuild("bu1"), dna.BaseBuild("bu13"), dna.BaseUpgrade(13),
               dna.BaseUpgrade(13), dna.BaseBuild("v", 4), dna.BaseBuild("w", 9),
               dna.BaseUpgrade(1)
        ]
        self.assertTrue(dna.DNA.validate_list(lst))
    
    def test_validation_list_failures(self):
        #TODO: This test.
        l1 = [dna.BaseBuild("bv2"), dna.BaseBuild("bu2")]
        #Invalid build location
        self.assertRaises(dna.DNAInvalidBuildLocation, dna.DNA, "bv2bu2")
        #Invalid upgrade location
        self.assertRaises(dna.DNAInvalidUpgradeLocation, dna.DNA, "bv2u3")
    
    def test_mutate_remove(self):
        d = dna.DNA("bu4bu2bv3u3")
        
        d = d.mutate_remove(1)
        self.assertEqual(str(d), "bu4bv3u3")
        
        self.assertRaises(dna.DNAInvalidUpgradeLocation, d.mutate_remove, 1)
    
    def test_mutate_insert(self):
        d = dna.DNA("bu1")
        
        b1 = dna.BaseBuild(dna.Tower.blue, 12)
        b2 = dna.BaseUpgrade(1)
        d = d.mutate_insert(1, b1)
        d = d.mutate_insert(1, b2)
        self.assertEqual(str(d), "bu1u1bu12")
        
        b3 = dna.BaseUpgrade(2)
        with self.assertRaises(dna.DNAInvalidUpgradeLocation) as cm:
            d.mutate_insert(2, b3)
        the_exception = cm.exception
        self.assertEqual(the_exception.base_loc, 2)
        
    
    def test_mutate_replace(self):
        d = dna.DNA("bu1u1")
        
        b1 = dna.BaseBuild(dna.Tower.blue, 2)
        b2 = dna.BaseUpgrade(2)
        
        with self.assertRaises(dna.DNAInvalidUpgradeLocation) as cm:
            d = d.mutate_replace(0, b1)
        the_exception = cm.exception
        self.assertEqual(the_exception.base_loc, 1)
        
        with self.assertRaises(dna.DNAInvalidUpgradeLocation) as cm:
            d = d.mutate_replace(1, b2)
        the_exception = cm.exception
        self.assertEqual(the_exception.base_loc, 1)
        
        d = dna.DNA("bu1bu2u1")
        d = d.mutate_replace(2, b2)
        self.assertEqual(str(d), "bu1bu2u2")
    
    def test_mutate(self):
        #Since randomness is used, repeat to ensure
        cur_s = "bu1bu2bu3u1u2u3"
        d = dna.DNA(cur_s)
        for i in range(1000):
            d = d.mutate()
            new_s = str(d)
            self.assertNotEqual(new_s, cur_s, d)
            d.validate()
            cur_s = new_s
    
    def test_first_yellow_fail(self):
        #Yellow(w) tower cannot be first since there is not enough money
        s = "bw4u4"
        self.assertRaises(dna.DNAInvalidBuildLocation, dna.DNA, s)
    

#TOOD: Test score function (and use of planet) in step
class VillageTests(unittest.TestCase):
    def test_to_string(self):
        d1 = dna.DNA.from_string("bu1bv2bw3")
        d2 = dna.DNA.from_string("bu1u1u1u1")
        d3 = dna.DNA.from_string("bv2u2")
        d4 = dna.DNA.from_string("bu1u1bw2")
        d5 = dna.DNA.from_string("bv9u9u9")
        v = dna.Village([
            (d1, None),
            (d2, None),
            (d3, 12),
            (d4, 35),
            (d5, 960)
        ])

        output_s = str(v)
        real_s = ":bu1bv2bw3\n"+\
        ":bu1u1u1u1\n"+\
        "12:bv2u2\n"+\
        "35:bu1u1bw2\n"+\
        "960:bv9u9u9"
        
        self.assertEqual(output_s, real_s)
    
    def test_from_string(self):
        s = ":bu1bv2bw3\n"+\
        ":bu1u1u1u1\n"+\
        "12:bv2u2\n"+\
        "35:bu1u1bw2\n"+\
        "960:bv9u9u9"
        
        v = dna.Village.from_string(s)
        
        real_v = dna.Village([
            (dna.DNA().from_string("bu1bv2bw3"), None),
            (dna.DNA().from_string("bu1u1u1u1"), None),
            (dna.DNA().from_string("bv2u2"), 12),
            (dna.DNA().from_string("bu1u1bw2"), 35),
            (dna.DNA().from_string("bv9u9u9"), 960)
        ])
        
        self.assertEqual(v.dnas, real_v.dnas)
    
    def test_step(self):
        s = ":bu7bu8\n"+\
        ":bu6"
        
        v = dna.Village.from_string(s)
        v.set_score_func(lambda x: None)
        
        #Test that returning None as a score gives empty score
        out1 = v.step()
        self.assertEqual(out1, True)
        
        self.assertEqual(str(v.dnas[0][0]), "bu7bu8")
        self.assertEqual(v.dnas[0][1], None)
        
        #Test that scores change
        v.set_score_func(lambda x: int(str(x)=="bu7bu8"))
        out1 = v.step()
        self.assertEqual(out1, True)
        
        self.assertEqual(str(v.dnas[0][0]), "bu7bu8")
        self.assertEqual(v.dnas[0][1], 1)
        self.assertEqual(str(v.dnas[1][0]), "bu6")
        self.assertIsNone(v.dnas[1][1])
        
        out2 = v.step()
        self.assertEqual(out2, False)
        
        self.assertEqual(str(v.dnas[0][0]), "bu7bu8")
        self.assertEqual(v.dnas[0][1], 1)
        self.assertEqual(str(v.dnas[1][0]), "bu6")
        self.assertEqual(v.dnas[1][1], 0)
        
        out3 = v.step() #Creating next generation now
        self.assertEqual(out3, True)
        
        self.assertEqual(str(v.dnas[0][0]), "bu7bu8")
        self.assertEqual(v.dnas[0][1], 1)
        self.assertNotEqual(str(v.dnas[1][0]), "bu6")
        self.assertIsNone(v.dnas[1][1])
    
    def test_next_generation_odd(self):
        #Top 5 DNAS have quad-digit scores
        #Bottom 6 DNAs have double-digit scores
        s = "1111:bu4bu5bu6bu7\n"+\
        "11:bu1bv2bw3u2u3u1\n"+\
        "2222:bu2bv4bw3u2\n"+\
        "22:bv8u8u8u8u8u8u8\n"+\
        "3333:bv4bv5bv6u4u5u6\n"+\
        "33:bu1bu2bu3bu4bu5bu6bu7bu8bu9\n"+\
        "4444:bu1u1u1u1u1u1u1u1u1u1u1u1u1u1\n"+\
        "44:bu2bu1u1u1u1u1u1u1u1u1u1u1u1\n"+\
        "5555:bu5bv6bu7u5u7u5u7u6\n"+\
        "55:bv9u9u9u9bu7u7u7u7\n"+\
        "66:bu1bu9bv2bv8u1u9u8u9" #Is completely replaced
        
        v = dna.Village.from_string(s)
        
        v.develop_next_gen()
        
        self.assertEqual(str(v.dnas[0][0]), "bu5bv6bu7u5u7u5u7u6")
        self.assertEqual(v.dnas[0][1], 5555)
        self.assertEqual(str(v.dnas[1][0]), "bu1u1u1u1u1u1u1u1u1u1u1u1u1u1")
        self.assertEqual(v.dnas[1][1], 4444)
        self.assertEqual(str(v.dnas[2][0]), "bv4bv5bv6u4u5u6")
        self.assertEqual(v.dnas[2][1], 3333)
        self.assertEqual(str(v.dnas[3][0]), "bu2bv4bw3u2")
        self.assertEqual(v.dnas[3][1], 2222)
        self.assertEqual(str(v.dnas[4][0]), "bu4bu5bu6bu7")
        self.assertEqual(v.dnas[4][1], 1111)
        self.assertNotEqual(str(v.dnas[5][0]), "bu1bu9bv2bv8u1u9u8u9")
        self.assertIsNone(v.dnas[5][1])
        self.assertNotEqual(str(v.dnas[6][0]), "bv9u9u9u9bu7u7u7u7")
        self.assertIsNone(v.dnas[6][1])
        self.assertNotEqual(str(v.dnas[7][0]), "bu2bu1u1u1u1u1u1u1u1u1u1u1u1")
        self.assertIsNone(v.dnas[7][1])
        self.assertNotEqual(str(v.dnas[8][0]), "bu1bu2bu3bu4bu5bu6bu7bu8bu9")
        self.assertIsNone(v.dnas[8][1])
        self.assertNotEqual(str(v.dnas[9][0]), "bv8u8u8u8u8u8u8")
        self.assertIsNone(v.dnas[9][1])
        self.assertNotEqual(str(v.dnas[10][0]), "bu1bv2bw3u2u3u1")
        self.assertIsNone(v.dnas[10][1])
    
    def test_next_gen_even(self):
        #Top 5 DNAS have quad-digit scores
        #Bottom 5 DNAs have double-digit scores
        s = "1111:bu4bu5bu6bu7\n"+\
        "11:bu1bv2bw3u2u3u1\n"+\
        "2222:bu2bv4bw3u2\n"+\
        "22:bv8u8u8u8u8u8u8\n"+\
        "3333:bv4bv5bv6u4u5u6\n"+\
        "33:bu1bu2bu3bu4bu5bu6bu7bu8bu9\n"+\
        "4444:bu1u1u1u1u1u1u1u1u1u1u1u1u1u1\n"+\
        "44:bu2bu1u1u1u1u1u1u1u1u1u1u1u1\n"+\
        "5555:bu5bv6bu7u5u7u5u7u6\n"+\
        "55:bv9u9u9u9bu7u7u7u7"
        
        v = dna.Village.from_string(s)
        
        v.develop_next_gen()
        
        self.assertEqual(str(v.dnas[0][0]), "bu5bv6bu7u5u7u5u7u6")
        self.assertEqual(v.dnas[0][1], 5555)
        self.assertEqual(str(v.dnas[1][0]), "bu1u1u1u1u1u1u1u1u1u1u1u1u1u1")
        self.assertEqual(v.dnas[1][1], 4444)
        self.assertEqual(str(v.dnas[2][0]), "bv4bv5bv6u4u5u6")
        self.assertEqual(v.dnas[2][1], 3333)
        self.assertEqual(str(v.dnas[3][0]), "bu2bv4bw3u2")
        self.assertEqual(v.dnas[3][1], 2222)
        self.assertEqual(str(v.dnas[4][0]), "bu4bu5bu6bu7")
        self.assertEqual(v.dnas[4][1], 1111)
        self.assertNotEqual(str(v.dnas[5][0]), "bv9u9u9u9bu7u7u7u7")
        self.assertIsNone(v.dnas[5][1])
        self.assertNotEqual(str(v.dnas[6][0]), "bu2bu1u1u1u1u1u1u1u1u1u1u1u1")
        self.assertIsNone(v.dnas[6][1])
        self.assertNotEqual(str(v.dnas[7][0]), "bu1bu2bu3bu4bu5bu6bu7bu8bu9")
        self.assertIsNone(v.dnas[7][1])
        self.assertNotEqual(str(v.dnas[8][0]), "bv8u8u8u8u8u8u8")
        self.assertIsNone(v.dnas[8][1])
        self.assertNotEqual(str(v.dnas[9][0]), "bu1bv2bw3u2u3u1")
        self.assertIsNone(v.dnas[9][1])
    
    def test_1_village(self):
        s = "10:bu7bu8"
        v = dna.Village.from_string(s)
        
        v.develop_next_gen()
        
        self.assertNotEqual(str(v.dnas[0][0]), "bu7bu8")
        self.assertIsNone(v.dnas[0][1])


class VillageFileTests(unittest.TestCase):
    EXAMPLE_VILLAGE = "data/example_village.txt"
    EXAMPLE_VILLAGE_S = """23:bu7bv8bw9
99:bu8u8u8u8u8u8u8
113:bu3bw9bw4u4bu2
:bu3bv9bw4bw1bu6u9
117:bu3bw9bu2bu6bu7
:bu3bw4bu2bu6
1000:bu1"""
    
    def setUp(self):
        with open(self.EXAMPLE_VILLAGE, 'w') as f:
            f.write(self.EXAMPLE_VILLAGE_S)
    
    def test_load_from_file(self):
        vf = dna.VillageFile(self.EXAMPLE_VILLAGE)
        self.assertEqual(str(vf), self.EXAMPLE_VILLAGE_S)
    
    def test_update_to_file(self):
        vf = dna.VillageFile(self.EXAMPLE_VILLAGE)
        vf.set_score_func(lambda x: 5)
        vf.step()
        vf.step()
        
        expected_s = """23:bu7bv8bw9
99:bu8u8u8u8u8u8u8
113:bu3bw9bw4u4bu2
5:bu3bv9bw4bw1bu6u9
117:bu3bw9bu2bu6bu7
5:bu3bw4bu2bu6
1000:bu1"""
        
        with open(self.EXAMPLE_VILLAGE) as f:
            new_s = f.read()
        self.assertEqual(new_s, expected_s)
        

class PlanetTests(unittest.TestCase):
    
    def test_from_string_success(self):
        s = "89:bu7bu8u8u8\n\
        90:bu7u7u7\n\
        0:bu7bw9bv8u8u9u7"
        
        p = dna.Planet(s)
        
        self.assertEqual(str(p.known_dnas[0][0]), "bu7bu8u8u8")
        self.assertEqual(p.known_dnas[0][1], 89)
        self.assertEqual(str(p.known_dnas[1][0]), "bu7u7u7")
        self.assertEqual(p.known_dnas[1][1], 90)
        self.assertEqual(str(p.known_dnas[2][0]), "bu7bw9bv8u8u9u7")
        self.assertEqual(p.known_dnas[2][1], 0)
    
    def test_from_string_failure(self):
        self.assertRaises(dna.PlanetEmptyScore, dna.Planet, ":bu2")
        self.assertRaises(dna.DNAInvalidCreationString, dna.Planet, "1:ba1")
    
    def test_from_list(self):
        #Successful creation
        dnalst = [
            (dna.DNA("bu1bu2bu3"), 23),
            (dna.DNA("bu5bv2bu3"), 34),
            (dna.DNA("bu1u1bw2u2"), 45),
        ]
        p = dna.Planet(dnalst)
        
        self.assertEqual(str(p.known_dnas[0][0]), "bu1bu2bu3")
        self.assertEqual(p.known_dnas[0][1], 23)
        self.assertEqual(str(p.known_dnas[1][0]), "bu5bv2bu3")
        self.assertEqual(p.known_dnas[1][1], 34)
        self.assertEqual(str(p.known_dnas[2][0]), "bu1u1bw2u2")
        self.assertEqual(p.known_dnas[2][1], 45)
        
        #Failed Creation
        dnalst = [
            (dna.DNA("bv2u2u2bu1"), None),
        ]
        self.assertRaises(dna.PlanetEmptyScore, dna.Planet, dnalst)
    
    def test_to_string(self):
        s = "12:bu1bu2bu3\n"+\
        "11:bv2u2u2bw8\n"+\
        "10:bu8"
        
        p = dna.Planet(s)
        self.assertEqual(str(p), s)


class PlanetFileTests(unittest.TestCase):
    EXAMPLE_PLANET = "data/example_planet.txt"
    EXAMPLE_PLANET_S = """23:bu7bv8bw9
99:bu8u8u8u8u8u8u8
1029:bu1bv2bw3u1u2u3
113:bu3bw9bw4u4bu2
77:bu3bv9bw4bw1bu6u9
117:bu3bw9bu2bu6bu7
57:bu3bw4bu2bu6"""
    INVALID_PLANET = "data/invalid_planet.txt"
    INVALID_PLANET_S = """113:bu3bw9bw4u4bu2
:bu3bv9bw4bw1bu6u9
190:bu3bw9bu2bu6bu7
57:bu3bw4bu2bu6"""
    
    def setUp(self):
        #Write the example_planet.txt file and invalid_planet.txt file
        with open(self.EXAMPLE_PLANET, 'w') as f:
            f.write(self.EXAMPLE_PLANET_S)
        with open(self.INVALID_PLANET, 'w') as f:
            f.write(self.INVALID_PLANET_S)
    
    def test_read_from_file(self):
        pf = dna.PlanetFile(self.EXAMPLE_PLANET)
        self.assertEqual(str(pf), self.EXAMPLE_PLANET_S)
        
        #Invalid Planet
        self.assertRaises(dna.PlanetEmptyScore, dna.PlanetFile, self.INVALID_PLANET)
    
    def test_update_to_file(self):
        #Test an update that is done
        pf = dna.PlanetFile(self.EXAMPLE_PLANET)
        is_updated = pf.update("bu1", 1000)
        self.assertTrue(is_updated)
        with open(self.EXAMPLE_PLANET) as f:
            new_s = self.EXAMPLE_PLANET_S+"\n1000:bu1"
            self.assertEqual(f.read(), new_s)
        
        #Test an update that is skipped
        is_updated = pf.update("bu1", 2000)
        self.assertFalse(is_updated)
        with open(self.EXAMPLE_PLANET) as f:
            self.assertEqual(f.read(), new_s)
        
        #Test Multiple updates
        is_updated = pf.update("bu2", 2)
        self.assertTrue(is_updated)
        with open(self.EXAMPLE_PLANET) as f:
            new_s = new_s+"\n2:bu2"
            self.assertEqual(f.read(), new_s)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()