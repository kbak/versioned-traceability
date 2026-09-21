module ownership
sig User {}
sig Resource { owner: one User }
pred allowed[u: User, r: Resource] { u = r.owner }
assert OwnerOnly { all u: User, r: Resource | allowed[u, r] implies u = r.owner }
pred CanAccess { some u: User, r: Resource | allowed[u, r] }
check OwnerOnly for 3
run CanAccess for 3
