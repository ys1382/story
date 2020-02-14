import random
from statistics import mean


class Item:
    lot = []

    def __init__(self, name, traits=None):
        self.name = name
        if traits:
            self.traits = {c.name: c for c in traits}
            self.values = {trait.name: trait.value() for trait in self.traits.values()}
        else:
            self.traits = None
            self.values = {}
        self.inventory = []
        self.container = None

        Item.lot.append(self)

    def set(self, key, value):
        self.values[key.name] = value

    def take(self, what):
        if what.container:
            what.container.inventory.remove(what)
        self.inventory.append(what)
        what.container = self

    def __str__(self):
        kv = ['\n\t' + key + ': ' + str(self.values[key]) for key in self.values.keys()]
        return self.name + ':'.join(kv)


class Trait:
    def __init__(self, name, space):
        self.name = name
        self.space = space

    def value(self, set_to=None):
        if set_to is None:
            return Value(self, random.choice(list(self.space)))
        return Value(self, set_to)


class Value:
    def __init__(self, trait, value):
        self.trait = trait
        self.value = value

    def __str__(self):
        return self.value.name


class Goal:
    def __init__(self, item, key, value, weight=1):
        self.item_name = item.name
        self.key = key
        self.value = value
        self.weight = weight

    def met(self, instances):
        instance = instances[self.item_name].traits[self.key]
        if not instance:
            return 0
        reality = instances[self.item_name].traits[self.key].value
        wish = self.value
        conflict = abs(wish - reality)  # 0 for goal is met, 1 for not, in between for sort-of-met
        return self.weight * (1 - conflict)


class Verb:
    def __init__(self, name, act, can=None):
        self.name = name
        self.act = act
        self.can = can

    def do(self, subject, target):
        print(subject.name + ' ' + self.name + ' ' + target.name)
        self.act(subject, target)

    def available(self, who):
        if self.can:
            cans = list(filter(self.can(who), Item.lot))
            return cans
        print('lot')
        return Item.lot


class Agent(Item):
    cast = []

    def __init__(self, name, traits, verbs, goals):
        super().__init__(name, traits)
        self.verbs, self.goals = verbs, goals
        Agent.cast.append(self)

    def step(self):
        verb = random.choice(self.verbs)
        items = verb.available(self)
        if len(items) > 0:
            self.do(verb, random.choice(items))

    def do(self, verb, what):
        verb.do(self, what)

    def happiness(self, states=None):
        states = Item.lot
        return mean(list(map(lambda goal: goal.met(states), self.goals)))


class Setting:
    def __init__(self):
        self.instances = Item.lot

    def __str__(self):
        cast = list(filter(lambda instance: instance in Agent.cast, self.instances))
        return ''.join(['\n' + str(instance) for instance in cast])

    def step(self):
        cast = list(filter(lambda instance: instance in Agent.cast, self.instances))
        for agent in cast:
            agent.step()


#######

class Person(Agent):

    def __str__(self):
        stuff = '\n\tinventory: ' + ''.join([i.name for i in self.inventory]) if len(self.inventory) > 0 else ''
        where = Location.str(self.container)
        return super().__str__() + where + stuff

    class Go:
        @staticmethod
        def act(who, where):
            where.take(who)

        @staticmethod
        def can(who):
            # return lambda where: (where in location.space) and (who.values[location.name] != where)
            return Location.can(who)

    class Take:
        @staticmethod
        def act(who, what):
            who.take(what)

        @staticmethod
        def can(who):
            return lambda what: (what not in location.space) and (what != who) and (who.container == what.container)


class Location(Trait):
    def __init__(self):
        self.castle = Item("Castle")
        self.cave = Item("Cave")
        super().__init__("Location", [self.castle, self.cave])

    @staticmethod
    def str(where):
        return ('\n\tLocation: ' + str(where)) if (where in location.space) else Location.str(where.container) if where else ''

    @staticmethod
    def can(who):
        return lambda where: (where in location.space) and (who.container != where)


alive = Trait('alive', [Item("True"), Item("False")])


location = Location()
go = Verb('go', Person.Go.act, Person.Go.can)
take = Verb('take', Person.Take.act, Person.Take.can)
princess = Item('Princess', [])
princessInCastle = Goal(princess, location, location.castle)
prince = Person('Prince', [alive], [go, take], [princessInCastle])
princessInCave = Goal(princess, location, location.cave)
dragon = Person('Dragon', [alive], [take, go], [princessInCave])


def auto():
    setting = Setting()
    print(str(setting))
    setting.step()
    print(str(setting))


auto()
