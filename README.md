# graph-streaming

Mining data streams in the context of counting distinct elements in streams. The application is harmonic centrality estimation on streamed graph data with the [HyperBall algorithm](https://arxiv.org/pdf/1308.2144v2.pdf).
The HyperBall algorithm relies on [HyperLogLogCounters](http://algo.inria.fr/flajolet/Publications/FlFuGaMe07.pdf) for estimating the set size of distinct elements in data stream.

## Algorithm

The HyperLogLog algorithm is used to estimate a ball around node ```x``` at distance ```t```, that is, the number of nodes at distance ```t``` from ```x```. The difference of the ball size at distance ```t+1``` and ```t``` is used to compute the harmonic centrality of node ```x``` in the graph.
For more details, see the papers.

## Data

The datasets used in the project include the [email-Eu-core network data](http://snap.stanford.edu/data/email-Eu-core.html) and the [Wikipedia vote network data](http://snap.stanford.edu/data/wiki-Vote.html). Both are directed, unweighted graphs with 1005 and 7115 nodes, and 25571 and 103689 edges, respectively.
To download the datasets, run the ```data.sh``` bash script, or visit the URLs.

## Run

Install the dependencies in a virtual environment from the ```environment.yml``` file.
To run the HyperBall algorithm on a dataset with a certain precision (defined by the number of bits in the registers of the HyperLogLogCounters), run:

```
python3 main.py <dataset> <b>
```

where ```<dataset>``` is one of ```email``` or ```wiki``` for the aforementioned datasets. 

For example, to run the algorithm on the email dataset with 5 as the number of bits in the HyperLogLogCounters (precision=2^5=32), do:
```
python3 main.py "email" 5
```

which gives something similar to
```
reading data/email-Eu-core.txt
created graph with 1005 nodes and 25571 edges
HyperBall: b=5, p=32, len(g.nodes)=1005, len(g.edges)=25571
Fitting HyperBall ...
radius=1, convergence: 0.0000%, edges: : 100%|██████████| 25571/25571 [00:02<00:00, 12250.26it/s]                                                                                                          
radius=2, convergence: 99.3274%, edges: : 100%|██████████| 25571/25571 [00:02<00:00, 11894.10it/s]                                                                                                         
radius=3, convergence: 72.6761%, edges: : 100%|██████████| 25571/25571 [00:02<00:00, 11923.87it/s]                                                                                                         
radius=4, convergence: 87.6277%, edges: : 100%|██████████| 25571/25571 [00:02<00:00, 11839.55it/s]                                                                                                         
radius=5, convergence: 97.9513%, edges: : 100%|██████████| 25571/25571 [00:02<00:00, 12634.77it/s]                                                                                                         
radius=6, convergence: 99.9140%, edges: : 100%|██████████| 25571/25571 [00:02<00:00, 12254.68it/s]                                                                                                         
HyperBall converged
HyperBall execution time: 12.9835 seconds
fitting NetworkX.harmonic_centrality() ...
NetworkX execution time: 1.6200 seconds
HyperBall converged with an approximation error of 3.4193%
saved results to: assets/email.csv
script execution time: 14.6862 seconds
done!
```

or 

```
python3 main.py "wiki" 5
```

which gives something similar to
```
created graph with 7115 nodes and 103689 edges
plotting graph...
graph plotting execution time: 643.0444 seconds
HyperBall: b=5, p=32, len(g.nodes)=7115, len(g.edges)=103689
Fitting HyperBall ...
radius=1, convergence: 0.0000%, edges: : 100%|██████████| 103689/103689 [00:12<00:00, 8453.65it/s]                                                                                                         
radius=2, convergence: 98.8842%, edges: : 100%|██████████| 103689/103689 [00:12<00:00, 8375.25it/s]                                                                                                        
radius=3, convergence: 77.1046%, edges: : 100%|██████████| 103689/103689 [00:12<00:00, 7982.94it/s]                                                                                                        
radius=4, convergence: 84.3042%, edges: : 100%|██████████| 103689/103689 [00:12<00:00, 8054.97it/s]                                                                                                        
radius=5, convergence: 93.3514%, edges: : 100%|██████████| 103689/103689 [00:13<00:00, 7722.53it/s]                                                                                                        
radius=6, convergence: 97.3682%, edges: : 100%|██████████| 103689/103689 [00:12<00:00, 8198.47it/s]                                                                                                        
radius=7, convergence: 99.5873%, edges: : 100%|██████████| 103689/103689 [00:12<00:00, 8487.62it/s]                                                                                                        
radius=8, convergence: 99.9942%, edges: : 100%|██████████| 103689/103689 [00:12<00:00, 8250.29it/s]                                                                                                        
HyperBall converged
HyperBall execution time: 104.2652 seconds
NetworkX execution time: 25.9885 seconds
HyperBall converged with an approximation error of 4.0030%
saved results to: assets/wiki.csv
script execution time: 773.5685 seconds
done!
```

## Reproducibility

The ```PYTHONHASHSEED``` environment variable is fixed so that the built-in ```hash``` function yields consistent values across runs.


## Results

See the results at ```assets/email.csv``` and ```assets/wiki.csv``` where:
- ```id```: node IDs in graph and data
- ```true```: the true harmonic centrality values (as computed by the ```networkx.harmonic_centrality``` function)
- ```hb```: the estimated harmonic centrality values (as computed by the ```HyperBall``` algorithm)
- ```err[%]```: the approximation error of the HyperBall estimates to the true harmonic centralities, in percentage, as absolute relative error

Results on the email dataset (1005 nodes and 25571 edges):

|  | Execution Time (seconds) | Error [%] (compared to networkx)| 
| ----------- | ----------- | ----------- |
| HyperBall (b=4) | 9.2753 | 9.4024 |
| HyperBall (b=5) | 12.6544 | 3.4193 |
| NetworkX | 1.3376 | 0 |

Results on the wiki dataset (7115 nodes and 103689 edges):

|  | Execution Time (seconds) | Error [%] (compared to networkx)| 
| ----------- | ----------- | ----------- |
| HyperBall (b=4) | 88.3968 | 9.1198 |
| HyperBall (b=5) | 106.6898 | 4.0030 |
| NetworkX | 25.1015 | 0 |

The execution times are from single runs, and are merely to illustrate the trends discussed below.
As the tables show, HyperBall has a very low discrepancy when compared to the true values (networkx). As the parameter ```b``` is increased, the accuracy of HyperBall increases, and so does its execution time.
When run on the wiki dataset (approximately 7x nodes and 4x edges), its execution time is approx. x10, while the execution time of networkx is approx. x20. The accuracies remain comparable across datasets regardless of the graph size.
The tendencies are a follows:
- the parameter ```b``` affects the number of registers of the HyperLogLogCounters in the HyperBall algorithm, therefore the accuracy of the algorithm. Higher ```b``` results in more accurate estimates of the harmonic centralities of the nodes
- the execution time slowly increases as the graph size increases - which is one of teh points of teh HyperBall algorithm 