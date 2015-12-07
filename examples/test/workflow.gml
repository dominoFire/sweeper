graph [
  directed 1
  node [
    id 0
    label "Task:final_results"
  ]
  node [
    id 1
    label "Task:create_sysinfo"
  ]
  node [
    id 2
    label "Task:create_filelist"
  ]
  node [
    id 3
    label "Task:check_files"
  ]
  edge [
    source 1
    target 0
  ]
  edge [
    source 2
    target 0
  ]
  edge [
    source 3
    target 1
  ]
  edge [
    source 3
    target 2
  ]
]
