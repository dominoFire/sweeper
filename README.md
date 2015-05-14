# Sweeper

Workflow execution on cloud environments.

By [@dominofire](http://twitter.com/dominofire)



## TODO

 - [ ] Design workflow mechanism
     * [ ] Design YAML workflow specification
     * [x] Estimate how many VM's are required to run the workflow
     * [ ] Estimate the expected performance matrix (linear regression)
     * [ ] Provide parameter sweep mechanism
     * [ ] Create example for creating file system for cloud resources
     * [ ] Attach filesystem 
     * [ ] Take into account how to *estimate* memory usage in tasks
 - [-] Provide examples
 - [x] Resolve automation issues
     * It only remains the deletion of storage accounts 
 - [ ] Make a performance benchmark based in FLOPS
     * FLOPS will be our complexity factor, more flops, more speedy computer
     * SPEC CPU2006  benchmark is not free,
     * PerfKitBenchmarker by google,
     * It gives lots of info regarding trhoughput
 - [ ] Make a input-sensitive profiling of tasks
     * First, find out how to estimate in python scripts
 - [x] Execution driver
 - [-] Read paper on CSE
 - [ ] Future work and improvement areas
     * Dockerize workflow execution 



## Command design

Initialize the required data for a specific provider

```
sweeper init [azure|rax]
```

Profiles a workflow for generating better prediction about workflow execution cost

```
sweeper profile
```

Run the workflow

```
sweeper run
```



## Bibliography to read

 - B. C. Dean, M. X. Goemans, and J. Vondrak. Approximating the stochastic knapsack problem: The benefit of adaptivity. In Proceedings of FOCS’04, pages 208–217, 2004.
 - C. Derman, G. J. Lieberman, and S. M. Ross. A renewal decision problem. Management Science, 24(5):pp. 554–561, 1978
 - N. Karmarkar and R. M. Karp. An efficient approximation scheme for the one-dimensional bin-packing problem. In Proceedings of SFCS’82, pages 312–320, 1982.
