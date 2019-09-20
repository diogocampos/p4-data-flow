#include <core.p4>
#include <v1model.p4>

header ethernet_t {
    bit<48> dstAddr;
    bit<48> srcAddr;
    bit<16> etherType;
}

header ipv4_t {
    bit<4>  version;
    bit<4>  ihl;
    bit<8>  diffserv;
    bit<16> totalLen;
    bit<16> identification;
    bit<3>  flags;
    bit<13> fragOffset;
    bit<8>  ttl;
    bit<8>  protocol;
    bit<16> hdrChecksum;
    bit<32> src;
    bit<32> dst;
}

header l4_t {
    bit<16> src;
    bit<16> dst;
}

struct metadata {
}

struct headers {
    @name(".ethernet") 
    ethernet_t ethernet;
    @name(".ipv4") 
    ipv4_t     ipv4;
    @name(".l4") 
    l4_t       l4;
}

parser ParserImpl(packet_in packet, out headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {
    @name(".parse_ipv4") state parse_ipv4 {
        packet.extract(hdr.ipv4);
        transition select(hdr.ipv4.protocol) {
            8w0x6: parse_l4;
            8w0x11: parse_l4;
            default: accept;
        }
    }
    @name(".parse_l4") state parse_l4 {
        packet.extract(hdr.l4);
        transition accept;
    }
    @name(".start") state start {
        packet.extract(hdr.ethernet);
        transition select(hdr.ethernet.etherType) {
            16w0x800: parse_ipv4;
            default: accept;
        }
    }
}

control ingress(inout headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {
    @name("._drop") action _drop() {
        mark_to_drop(standard_metadata);
    }
    @name("._no_op") action _no_op() {
    }
    @name(".a_fwd") action a_fwd(bit<9> port) {
        standard_metadata.egress_spec = port;
    }
    @name(".l4_is_valid") action l4_is_valid() {
    }
    @name(".fw_dst") table fw_dst {
        actions = {
            _drop;
            _no_op;
        }
        key = {
            hdr.l4.dst: exact;
        }
    }
    @name(".fw_src") table fw_src {
        actions = {
            _drop;
            _no_op;
        }
        key = {
            hdr.l4.src: exact;
        }
    }
    @name(".fwd") table fwd {
        actions = {
            a_fwd;
        }
        key = {
            standard_metadata.ingress_port: exact;
        }
    }
    @name(".is_l4_valid") table is_l4_valid {
        actions = {
            l4_is_valid;
            _no_op;
        }
        key = {
            hdr.l4.isValid(): exact;
        }
    }
    apply {
        fwd.apply();
        switch (is_l4_valid.apply().action_run) {
            l4_is_valid: {
                switch (fw_src.apply().action_run) {
                    _no_op: {
                        fw_dst.apply();
                    }
                }

            }
        }

    }
}

control egress(inout headers hdr, inout metadata meta, inout standard_metadata_t standard_metadata) {
    apply {
    }
}

control DeparserImpl(packet_out packet, in headers hdr) {
    apply {
        packet.emit(hdr.ethernet);
        packet.emit(hdr.ipv4);
        packet.emit(hdr.l4);
    }
}

control verifyChecksum(inout headers hdr, inout metadata meta) {
    apply {
    }
}

control computeChecksum(inout headers hdr, inout metadata meta) {
    apply {
    }
}

V1Switch(ParserImpl(), verifyChecksum(), ingress(), egress(), computeChecksum(), DeparserImpl()) main;

