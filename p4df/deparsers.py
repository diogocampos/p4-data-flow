def do_deparsers(p4, flow):
    flow.push_node('deparsers')

    deparser = p4['deparsers'][0]
    for header_name in deparser['order']:
        flow.use_all(header_name)
