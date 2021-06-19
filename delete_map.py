import hazelcast

client = hazelcast.HazelcastClient(
    cluster_name="dev",
    cluster_members=[
        "172.17.0.4:5701",
        "172.17.0.5:5701",
    ]
)

client.get_map("lab6").destroy();
