from orm.api import Api


controller = Api('http://127.0.0.1:8888/api')
controller.enable_logging()
controller.server.retrieve()
nodes = controller.nodes.retrieve()
node = nodes[0]
print node.slivers.create(group=controller.groups.retrieve()[0])





################
# CREATE () 
#########################
# RELATEDCOLLECTION
node = controller.nodes.create()
# (slivers) = self.related_name
# (kwargs) = { self.parent.get_name(): self.parent }
# self.(api).(slivers).create((kwargs))
sliver = node.slivers.create()
#
node = controller.create(rel.SERVER_NODES)
# (slivers) = self.related_name
# (kwargs) = { self.parent.get_name(): self.parent }
# self.(api).(slivers).create((kwargs))
sliver = node.slivers.create()

# COLLECTION
slivers = controller.slivers.retrieve()
# (slivers) = get_name(self.uri)
# (slivers) = self._headers.content_type.get('schema')
# self.(api).(slivers).create()
sliver = slivers.create()
#
slivers = controller.retrieve(rel.SERVER_SLIVERS)
# (slivers) = get_name(self.uri)
# (slivers) = self._headers.content_type.get('schema')
# self.(api).(slivers).create()
sliver = slivers.create()
########################


############
# RETRIEVE ()
##################
# COLLECTION: self.uri
nodes = controller.nodes.retrieve()
nodes.retrieve()
# RELATEDCOLLECTION: ret node + ret slivers
slivers = node.slivers.retrieve()
slivers.retrieve()



#############
# DESTROY ()
######################
# COLLECTION
slivers = controller.slivers.retrieve()
slivers.destroy()
# RELATEDCOLLECTION
node = controller.nodes.retrieve(pk=1)[0]
node.slivers.destroy()


###########
# UPDATE ()
###################
slivers = controller.slivers.retrieve()
slivers.update()
slivers = node.slivers
slivers.update()
slivers.save()


#########
# BULK ()
#############
slivers = controller.slivers.retrieve()
slivers.bulk(method)


############
# Transaction-like implementation
################
successes, failures = slivers.update(a=b)
if filures:
    successes.update(b=a)


####################
# RESOURCESET
###################
resources = ResourceSet(slivers + nodes)
resources.destroy()
resources.retrieve()
resources.bulk()
resources.filter()

# Transaction-like implementation
resources = ResourceSet[Resource(name='rata-%s' % i ) for i in range(0, 100)])
successes, failuers = resources.bulk(lambda r: r.save())
if failures:
    successes.destroy()






#node.slivers.retrieve()
#print node.nodes




