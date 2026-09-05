# Separate workflow history from maintenance rewrites

**Status:** accepted

Ageroot keeps episodic and semantic source journals append-only during task
work while permitting explicit memory maintenance to rewrite them, preserving
upstream cleanup behavior and reducing long-term divergence. This replaces the
previous blanket append-only policy; candidate state and derived views may
change during workflow operations, but accepting knowledge remains an explicit
review action and never an automatic maintenance step. Implementations must
coordinate writers and maintenance so this boundary does not permit lost
concurrent writes or partially rewritten history.
