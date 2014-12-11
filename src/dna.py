'''
Created on 24 Feb 2012

@author: Qasim

Note: The from_string methods actually require a list,
["string", "string2"], with no newline characters.
The to_string methods will actually return a string like "bu7\nbu8u8"

A typical DNA string is 'bu7bw9bv1u7u7bu2'.
'''

import random
from collections import namedtuple

Tower = namedtuple('Tower', 'blue green yellow')('u', 'v', 'w')
_tls = 'l1 l2 l3 l4 l5 l6 l7 l8 l9 l10 l11 l12 l13 l14 l15 l16 l17 l18'
_tls += ' l19 l20 l21 l22 l23 l24 l25 l26 l27 l28 l29 l30 l31 l32'
TowerLocation = namedtuple('TowerLocation', _tls)(*range(1, 33))

class BaseBuildInvalidStringError(Exception):
    def __init__(self, s, location):
        self.s = s
        self.location = location
    def __str__(self):
        err = "Location {loc} in the string '{s}' is invalid. {msg}"
        if self.location == 0:
            return err.format(loc=self.location, s=self.s, msg="It must 'b'.")
        elif self.location == 1:
            return err.format(loc=self.location, s=self.s,
                              msg="It must be 'u', 'v', or 'w'")
        elif self.location == 2:
            return err.format(loc=self.location, s=self.s,
                              msg="It must be a number 1, 2, ..., 9")
        elif self.location >= 3:
            return err.format(loc="3+", s=self.s, msg="The string is too long.")


class BaseBuild(namedtuple('BaseBuild', 'tower_type location')):
    __slots__ = ()
    
    def __new__(cls, *args):
        if len(args) == 1:
            return cls.from_string(*args)
        else:
            return super(BaseBuild, cls).__new__(cls, *args)
    
    @classmethod
    def from_string(cls, s):
        """Return new BaseBuild instance built from the entire string.
        
        Raise BaseBuildInvalidStringError for invalid strings."""
        if len(s) >= 5:
            raise BaseBuildInvalidStringError(s, 3)
        if s[0] != 'b':
            raise BaseBuildInvalidStringError(s, 0)
        
        tower_type = s[1]
        try:
            t = {'u': Tower.blue, 'v': Tower.green, 'w': Tower.yellow}[tower_type]
        except KeyError:
            raise BaseBuildInvalidStringError(s, 1)
        
        location1 = s[2]
        try:
            location2 = s[3]
        except IndexError:
            location2 = ''
        
        try:
            location = int(location1+location2)
        except ValueError:
            raise BaseBuildInvalidStringError(s, 2)
        
        if location <= 0:
            raise BaseBuildInvalidStringError(s, 2)
        try:
            l = TowerLocation[location-1]
        except IndexError:
            raise BaseBuildInvalidStringError(s, 2)
        
        return BaseBuild(t, l)
    
    @classmethod
    def from_string_info(cls, s):
        """Return new BaseBuild instance and number of characters used.
        
        Raise BaseBuildInvalidStringError for failure."""
        if len(s) < 3:
            raise BaseBuildInvalidStringError(s, len(s))
        
        try:
            int(s[3])
        except (ValueError, IndexError):
            return cls.from_string(s[:3]), 3
        else:
            return cls.from_string(s[:4]), 4
    
    def __repr__(self):
        return 'b{0}{1}'.format(self.tower_type, self.location)


class BaseUpgradeInvalidStringError(Exception):
    def __init__(self, s):
        self.s = s
    def __str__(self):
        err = "Error building a BaseUpgrade from the string '{}'."
        return err.format(self.s)


class BaseUpgrade(namedtuple('BaseUpgrade', 'location')):
    __slots__=()
    
    @classmethod
    def from_string(cls, s):
        """Return a BaseUpgrade instance built from the entire string.
        
        Raise BaseUpgradeInvalidStringError for invalid strings"""
        if len(s) not in (2, 3) or s[0] != 'u':
            raise BaseUpgradeInvalidStringError(s)
        
        location1 = s[1]
        try:
            location2 = s[2]
        except IndexError:
            location2 = ''
        
        try:
            location = int(location1+location2)
        except ValueError:
            BaseUpgradeInvalidStringError(s)
        
        if location <= 0:
            raise BaseUpgradeInvalidStringError(s)
        
        try:
            loc = TowerLocation[location-1]
        except IndexError:
            raise BaseUpgradeInvalidStringError(s)
        
        return BaseUpgrade(loc)
    
    @classmethod
    def from_string_info(cls, s):
        """Return new BaseUpgrade instance and number of characters used.
        
        Raise BaseUpgradeInvalidStringError for failure."""
        if len(s) < 2:
            raise BaseBuildInvalidStringError(s, len(s))
        
        try:
            int(s[2])
        except (IndexError, ValueError):
            return cls.from_string(s[:2]), 2
        else:
            return cls.from_string(s[:3]), 3
    
    def __repr__(self):
        return "u{0}".format(self.location)


def get_random_base():
    random_location = random.choice(TowerLocation)
    randbase = random.choice([BaseBuild, BaseUpgrade])
    if randbase == BaseBuild:
        tower_type = random.choice(Tower)
        return BaseBuild(tower_type, random_location)
    elif randbase == BaseUpgrade:
        return BaseUpgrade(random_location)


class DNAException(Exception):
    pass

class DNAInvalidCreationString(DNAException):
    def __init__(self, s, loc):
        self.s = s
        self.loc = loc
    
    def __str__(self):
        err = "In string '{0}', there was an error at location {1}"
        return err.format(self.s, self.loc)

class DNAValidationError(DNAException):
    def __init__(self, dna, base_loc, reason):
        self.dna = dna
        self.base_loc = base_loc
        self.reason = reason
        
    def __str__(self):
        s = "The base at location(0+) {1} is invalid. {2} DNA: {0}"
        return s.format(self.dna, self.base_loc, self.reason)

class DNAInvalidBuildLocation(DNAValidationError):
    """There is already a tower at that location"""
    def __init__(self, dna, base_loc,
                 reason="There is already a tower at this location."):
        super().__init__(dna, base_loc, reason)

class DNAInvalidUpgradeLocation(DNAValidationError):
    """There is no tower at that location to upgrade."""
    def __init__(self, dna, base_loc,
                 reason = "There is no tower at that location to upgrade"):
        super().__init__(dna, base_loc, reason)

class DNAInvalidInitialTower(DNAInvalidBuildLocation):
    """You cannot have the yellow tower at the start"""
    def __init__(self, dna, base_loc,
                 reason = "First tower must be blue(u) or green(v) due to cost."):
        super().__init__(dna, base_loc, reason)

class DNA(tuple):
    """A tuple of DNA Base instructions (Base1, Base2, Base3, ..., BaseN)
    
    You can make the DNA from a list of base sequences,
    another DNA object or from a string.
    
    """
    __slots__ = ()
    
    def __new__(cls, str_or_lst=""):
        if isinstance(str_or_lst, str):
            return cls.from_string(str_or_lst)
        else:
            cls.validate_list(str_or_lst)
            return tuple.__new__(cls, str_or_lst[:])
    
    def mutate_remove(self, location):
        """Return DNA with the base at the location (0+) removed (and validates)"""
        dna_list = list(self)
        del dna_list[location]
        return DNA(dna_list)
    
    def mutate_insert(self, location, base):
        """Return DNA with the base added at the location (0+) (and validates)"""
        dna_list = list(self)
        dna_list.insert(location, base)
        return DNA(dna_list)
    
    def mutate_replace(self, location, base):
        """Return DNA with base at given location replaced with new base (and validates)"""
        dna_list = list(self)
        dna_list[location] = base
        return DNA(dna_list)
    
    
    def mutate(self):
        """Return a new, mutated DNA object based on the current DNA.
        
        The mutation is guaranteed to be valid, different and non-empty."""
        #Ensure all positions have a tower in them
        unbuilt_locs = [loc for loc in TowerLocation]
        for base in self:
            if isinstance(base, BaseBuild):
                unbuilt_locs.remove(base.location)
        
        new_dna = list(self)
        for unbuilt_loc in unbuilt_locs:
            towertype = random.choice(Tower)
            insert_loc = random.randrange(0, len(self)+1)
            new_dna.insert(insert_loc, BaseBuild(towertype, unbuilt_loc))
        #First tower must be green or blue.
        if new_dna[0].tower_type not in (Tower.blue, Tower.green):
            tt = random.choice((Tower.blue, Tower.green))
            new_dna[0] = BaseBuild(tt, new_dna[0].location)
        new_dna = DNA(new_dna)
        
        #Now mutate
        while True:
            choices = [self.mutate_insert]*3 + [self.mutate_remove] + \
                      [self.mutate_replace]*2
            mutation = random.choice(choices)
            if mutation == self.mutate_insert:
                #Insert an upgrade tower somewhere
                upgrade_loc = random.choice(TowerLocation)
                for i, base in enumerate(new_dna):
                    if base.location == upgrade_loc:
                        start_loc = i+1
                        break
                insert_loc = random.randrange(start_loc, len(new_dna)+1)
                base = BaseUpgrade(upgrade_loc)
                new_dna = new_dna.mutate_insert(insert_loc, base)
                return new_dna
            elif mutation == self.mutate_remove:
                #Remove a random upgrade tower
                upgrade_poses = []
                for i, base in enumerate(new_dna):
                    if isinstance(base, BaseUpgrade):
                        upgrade_poses.append(i)
                if not upgrade_poses:
                    continue
                new_dna = new_dna.mutate_remove(random.choice(upgrade_poses))
                return new_dna
            elif mutation == self.mutate_replace:
                #Replace a build tower with a different tower type
                build_poses = []
                for i, base in enumerate(new_dna):
                    if isinstance(base, BaseBuild):
                        build_poses.append(i)
                random_pos = random.choice(build_poses)
                random_tower = new_dna[random_pos]
                if random_pos == 0:
                    tt_choices = [Tower.blue, Tower.green]
                else:
                    tt_choices = list(Tower)
                tt_choices.remove(random_tower.tower_type)
                tt = random.choice(tt_choices)
                new_build = BaseBuild(tt, random_tower.location)
                new_dna = new_dna.mutate_replace(random_pos, new_build)
                return new_dna
    
    
    def validate(self):
        return self.validate_list(self)
    
    @classmethod
    def validate_list(cls, lst):
        """Return whether a sequence of bases is a valid DNA string
        
        Raise various DNAValidationError stating what is incorrect"""
        if len(lst) == 0:
            return True
        locs = [] #Locations that towers have been built
        
        #Not enough money for this tower initially
        if isinstance(lst[0], BaseBuild):
            if lst[0].tower_type not in (Tower.blue, Tower.green):
                raise DNAInvalidInitialTower(lst, 0)
        
        for i, base in enumerate(lst): #i starts at 0
            if isinstance(base, BaseBuild):
                if base.location in locs:
                    raise DNAInvalidBuildLocation(lst, i)
                locs.append(base.location)
            elif isinstance(base, BaseUpgrade):
                if base.location not in locs:
                    raise DNAInvalidUpgradeLocation(lst, i)
        
        return True
    
    @classmethod
    def from_string(cls, s):
        """Return a DNA instance built from a string."""
        recorded_dna = []
        s_used_total = 0
        while s != "":
            fail = True
            try:
                new_base, s_used = BaseBuild.from_string_info(s)
            except BaseBuildInvalidStringError:
                pass
            else:
                fail = False
            
            if fail:
                try:
                    new_base, s_used = BaseUpgrade.from_string_info(s)
                except BaseUpgradeInvalidStringError:
                    pass
                else:
                    fail = False
            
            if fail:
                #No base matched the string
                raise DNAInvalidCreationString(s, s_used_total)
            else:
                recorded_dna.append(new_base)
                s_used_total += s_used
                s = s[s_used:]
        
        d = DNA(recorded_dna) #Create DNA by a list
        return d
    
    def __str__(self):
        s = ""
        for base in self:
            s += str(base)
        return s


class Village:
    """String format for a village is
    
    123:bu7u7
    98:bw8
    :bw9u9
    (score: DNA string)
    
    A score of "" (empty) means the DNA has not been scored.
    
    The planet is used to check if a DNA is scored before using score_func
    in order to score it.
    
    Internal: self.dnas = [((DNA Object, Score), ...]
    """
    
    def __init__(self, str_or_lst="", planet=None, score_func=None):
        if isinstance(str_or_lst, str):
            self.dnas = self.from_string(str_or_lst).dnas
        else:
            self.dnas = str_or_lst[:] #Must make copy of list of (dnas, score)
        self.planet = planet
        self.score_func = score_func
    
    def set_planet(self, planet):
        self.planet = planet
    
    def set_score_func(self, score_func):
        self.score_func = score_func
    
    def step(self):
        """Do a step of the village - THIS IS THE MAIN FUNCTION
        
        This will score DNAs which are not already scored and also develop
        the next generation of DNAs when appropriate.
        
        Returns:
            True - There is an unscored DNA left
            False - The next step will develop next generation
        """
        
        def get_unscored():
            num_unscored = 0
            for dna, score in self.dnas:
                if score is None:
                    num_unscored += 1
            return num_unscored
        
        if get_unscored() == 0:
            self.develop_next_gen()
            return True
        else:
            for i, dna_info in enumerate(self.dnas):
                dna, score = dna_info
                if score is None:
                    if self.planet is None:
                        score = self.score_func(dna)
                    else:
                        prior_score = self.planet.check_against(dna)
                        if prior_score is False:
                            score = self.score_func(dna)
                            if score is not None:
                                self.planet.update(dna, score)
                        else:
                            score = prior_score
                    break
            self.dnas[i] = (dna, score)
            
            if get_unscored() == 0:
                return False
            else:
                return True
    
    
    def develop_next_gen(self):
        """Develop the next generation of DNAs
        
        This will take the top 50% of DNAs, mutate them. The next generation
        is the top 50% plus the mutated 50%. For an odd number of DNAs,
        less than half of the village will be conserved.
        
        Following has been altered.
         (with a 10% chance
        of a large mutation occurring).
         The last ranking top DNA will be replaced
        by its mutation.
        A large mutation is 15 standard mutations.
        The mutated DNA is definitely to be different from the original DNA.
        
        Note: Every DNA must have a score otherwise the village cannot be sorted.
        """
        
        village_size = len(self.dnas)
        self.dnas.sort(key=lambda tup: tup[1], reverse=True) #Descending
        
        if village_size % 2 == 0:
            mutate_num = int(village_size/2)
            top_dnas = self.dnas[:mutate_num]
        else:
            mutate_num = int((village_size + 1) / 2)
            top_dnas = self.dnas[:mutate_num] #Remove the last top dna at the end
        
        new_dnas = []
        for i in range(mutate_num):
            base_dna = top_dnas[i][0]
            new_dna = base_dna.mutate()
            if random.random() < 1: #Large mutation
                for j in range(14):
                    new_dna = new_dna.mutate()
            if random.random() < 0.1:
                for j in range(99):
                    new_dna = new_dna.mutate()
            new_dnas.append((new_dna, None))
        
        if village_size % 2 == 0:
            self.dnas = top_dnas
        else:
            self.dnas = top_dnas[:-1]
        self.dnas.extend(new_dnas)
    
    @classmethod
    def from_string(cls, s):
        if s == "":
            return Village()
        
        str_lines = s.split("\n")
        dna_score_list = []
        
        for line in str_lines:
            score, dna = line.split(":")
            try:
                scorenum = int(score)
            except ValueError:
                scorenum = None
            d = DNA.from_string(dna)
            dna_score_list.append((d, scorenum))
        
        return Village(dna_score_list)
    
    def __repr__(self):
        s = ""
        for i, dna_info in enumerate(self.dnas):
            dna, score = dna_info
            if score is None:
                scoretxt = ""
            else:
                scoretxt = str(score)
            #Last line should not have newline char
            if i != len(self.dnas)-1:
                s += "{0}:{1}\n".format(scoretxt, str(dna))
            else:
                s += "{0}:{1}".format(scoretxt, str(dna))
        return s


class VillageFile(Village):
    def __init__(self, file_location, planet=None, score_func=None):
        self.file_location = file_location
        with open(file_location) as f:
            village_str = f.read()
        
        super(VillageFile, self).__init__(village_str, planet, score_func)
    
    def step(self):
        retval = super(VillageFile, self).step()
        
        with open(self.file_location, 'w') as f:
            f.write(str(self))
        
        return retval


class PlanetException(Exception):
    pass

class PlanetEmptyScore(PlanetException):
    """The list used to create the planet is invalid due to an unscored DNA."""
    
    def __init__(self, given_list, incorrect_item):
        self.given_list = given_list
        self.incorrect_item = incorrect_item
    
    def __str__(self):
        s = "The invalid item was (due to empty score): {0}.\n\n\
        The complete input was:\n\n{1}"
        return s.format(self.incorrect_item, self.given_list)

class PlanetInvalidUpdate(PlanetException):
    def __init__(self, dna, score):
        self.dna = dna
        self.score = score
    def __str__(self):
        s = "This update {0}:{1} is invalid because the score must be a number."
        s = s.format(self.score, self.dna)
        return s


class Planet:
    """A global storage of DNAs with known scores"""
    
    def __init__(self, str_or_lst=""):
        if isinstance(str_or_lst, str):
            self.validate_string(str_or_lst)
            v = Village.from_string(str_or_lst)
            self.known_dnas = v.dnas[:]
        else:
            self.validate_list(str_or_lst)
            self.known_dnas = str_or_lst[:]
    
    def update(self, dna, score):
        """Return whether the planet was updated with the new data."""
        if score is None:
            raise PlanetInvalidUpdate(dna, score)
        if dna not in [dna for dna, score in self.known_dnas]:
            self.known_dnas.append((dna, score))
            return True
        return False
    
    def check_against(self, dna):
        """Return the score if it is stored otherwise False"""
        for stored_dna, score in self.known_dnas:
            if stored_dna == dna:
                return score
        return False
    
    @classmethod
    def validate_list(cls, l):
        for i, dna_info in enumerate(l):
            score = dna_info[1]
            if score is None:
                raise PlanetEmptyScore(l[:], dna_info)
        return True
    
    @classmethod
    def validate_string(cls, s):
        v = Village.from_string(s)
        #Ensure every dna has a valid score
        for i, dna_info in enumerate(v.dnas):
            score = dna_info[1]
            if score is None:
                raise PlanetEmptyScore(s, s[i])
        
        return True
    
    def __str__(self):
        v = Village(self.known_dnas)
        return str(v)


class PlanetFile(Planet):
    """A global storage of scored DNAs into a file.
    
    This will update the file as appropriate automatically."""
    
    def __init__(self, file_location):
        self.file_location = file_location
        
        with open(file_location) as planet_file:
            s = planet_file.read()
        
        super(PlanetFile, self).__init__(s)
    
    def update(self, dna, score):
        """Return whether an update with the data provided occurred
        
        Updates the file as appropriate."""
        did_update = super(PlanetFile, self).update(dna, score)
        if did_update:
            with open(self.file_location, 'a') as pf:
                pf.write("\n{0}:{1}".format(score, str(dna)))
        return did_update
    
