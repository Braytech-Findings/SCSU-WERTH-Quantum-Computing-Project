# Metrics

The main architecture-comparison metrics are:

- logical depth;
- routed depth;
- native-compiled depth;
- routing SWAP count;
- native entangling-gate count;
- estimated native execution duration;
- estimated success probability;
- unsupported native-operation count;
- logical-to-native equivalence status.

Supporting simulator-style fields, such as count-to-probability conversion, total
variation distance, and Hellinger fidelity, are retained for the ideal/reference
workflow. The IBM proxy and Quantinuum proxy rows in the final architecture comparison
are offline proxy-model compilation and modeling results, not measured hardware
probability distributions.

Estimated native execution duration is derived from the proxy timing assumptions in
`results/tables/proxy_assumptions_table.csv`. Estimated success probability is derived
from the proxy error-rate assumptions in the same table. Neither metric is a measured
hardware result.
