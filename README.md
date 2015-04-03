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
 - [ ] Provide examples
 - [ ] Resolve all automation issues
 - [ ] Make a performance benchmark based in FLOPS
    * FLOPS will be our complexity factor, more flops, more speedy computer
    * SPEC CPU2006  benchmark is not free,
    * PerfKitBenchmarker by google,
    * It gives lots of info regarding trhoughput
 - [ ] Make a input-sensitive profiling of tasks
    * First, find out how to estimate in python scripts
 - [ ] Execution driver
 - [ ] Read paper on CSE
