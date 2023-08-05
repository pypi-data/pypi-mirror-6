import snakes.plugins
snakes.plugins.load(["ops","pids","let","gv"], "snakes.nets", "snk")
from snk import *
# n = PetriNet("n")
# n.add_place(Place("p", range(3)))
# n.add_transition(Transition('t', Expression("let(v=x+1) and v < 2")))
# n.add_input("p", "t", Variable('x'))
# t = n.transition("t")
# print t.modes()

net = PetriNet('SG')

net.add_transition(Transition("nextevent",
                              Expression('len(s) > 0 and let("req, s2=s[0], s[1:]", __raise__=True)'),
                              pids="h=j.new()"), status=Status("nextevent"))
net.add_transition(Transition("consumeret", status=Status("consumeret")))

net.add_place(Place("scenario",   status=Status("scenario")))
net.add_place(Place("scenarwait", status=Status("scenarwait")))
net.add_place(Place("pendings",   status=buffer("pendings")))
net.add_place(Place("returns",    status=buffer("returns")))
net.add_place(Place("nexttoken",  ['dot'], status=Status("nexttoken")))

net.add_input("scenario",    "nextevent", Tuple([ Variable('j'), Variable('s') ]))
net.add_input("nexttoken",   "nextevent", Value('dot'))
net.add_output("scenario",   "nextevent", Tuple([ Variable('j'), Variable('s2') ]))
net.add_output("pendings",   "nextevent", Tuple([ Variable('j'), Variable('req'), Variable('h') ]))
net.add_output("scenarwait", "nextevent", Tuple([ Variable('j'), Variable('h') ]))

net.add_input("scenarwait", "consumeret", Tuple([ Variable('j'), Variable('h') ]))
net.add_input("returns",    "consumeret", Tuple([ Variable('j'), Variable('rep'), Variable('h') ]))
net.add_output("nexttoken", "consumeret", Value('dot'))

net.place(net.nextpids).tokens.add([(Pid(1), 0), (Pid(2), 0)])
net.place("scenario").tokens.add([(Pid(1),"foo"), (Pid(1),"bar")])

net.draw(",let.png")

for mode in net.transition("nextevent").modes() :
    print mode
