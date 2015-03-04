# AAMAS 2015 experiments 

This repository contains the necessary information to reproduce the experiments presented at the AAMAS 2015 "Efficient Inter-Team Task Allocation in RoboCup Rescue" paper. This includes an admittedly convoluted explanation as well as the settings and scenarios used to produce the results.

Scenarios
---------

A scenario file in `RSLBench` defines the map where the simulation will run, the available number of agents (firefighters and/or police forces), as well as the roads that will be blocked at the beginning of the simulation. For this paper, we experimented mainly with the following scenario files (included in the `scenarios` folder):

- **official-2013.xml**, the paris scenario used in the 2013 RoboCup competition, including 40 firefighters at the competition's preset start locations. This scenario does not include any police forces nor any blockades (used in the initial results comparison without multiple teams).
- **official-2013-rblockades.xml**, the above scenario plus 25 police forces and blocked roads.
- **no-33-20-2013-rblockades.xml**, also in paris and with the same blocked roads than the previous scenario, but with only 33 firefighters and 20 police patrols.
- **no-27-15-2013-rblockades.xml**, also the same map and blocked roads, but with only 27 firefighters and 15 police patrols.
- **no-21-10-2013-rblockades.xml**, same map, same blocked roads, 21 firefighters and 10 police patrols.
- **no-15-5-2013-rblockades.xml**, the same as above but with even less firefighters (15) and police patrols (5).

Configuration settings
----------------------

Most of the configuration settings used for all experiments are the same, except for a few parameters. The file names identify which are these parameters. For instance, `paris-BinaryMaxSum-itno-t25-d0.0-gno.cfg` represents a configuration to run `BinaryMaxSum` in the `paris` map, with some particularities:

- **itno** means "interteam: no". Hence, in this case the teams would not coordinate between them.
- **t25** means "start-time: 25", which is the number of simulation steps that agents wait before doing anything (to give time for the fires to spread). The larger this value, the harder the scenario becomes.
- **d0.0** means "damping: 0.0", which represents the amount of damping used in BinaryMaxSum. Due to how it operates, a *0.0* damping is actually no damping at all.
- **gyes** meands "greedy_correction: yes", which enables the sequential greedy improvement over the solution found by the algorithm (as described in the paper).

Configuration settings for the `DSA` algorithm have two particular settigns that other algorithms do not have, namely:

- **p0.1** means that DSA will use a `p` value of 0.1 under this configuration.
- **tglast** represents "dsa.initial_target: last", where agents start the algorithm by picking the target they were assigned during the last simulation step. Alternatives include "best" (where agents tart picking the greedily best target for them) and "random", where they pick a random target to bootstrap the algorithm.


Raw results
-----------

To reproduce all results, 30 simulations (with different random seeds) must be run for each of the configurations in the `configurations` folder on each of the scenarios in the `scenarios` folder. This would produce the 12390 raw result files (30*59*6) which have been used in the experimental evaluation of the paper.

Furthermore, each simulation takes around 5 min. to complete, and requires a hefty amount of available RAM memory (meaning that running simulations in parallel is a bad idea). Thus, the `results` folder in this repository includes the 750 (30 runs * 5 maps * 5 algorithms) result files used to produce the graphs shown in the paper. We intentionally left out the other results (used to pick the best *p* value for `DSA` and the best *damping* value for BMS) due to space limitations.

These raw result files contain per-iteration metrics for each run, which is a *large* amount of information. Being text files, they can be processed using any scripting or analysis tools. In our case, we developed a few python scripts to exctract aggregated metrics and plot them.


Scripts
-------

The scripts we used can be found in the `scripts` folder. *Python 2.6* or newer is required, as well as the following python libraries:

- `numpy` for numeric matrix manipulation.
- `scipy` for statistical computations.
- `matplotlib` to produce plot figures.

The scripts used to produce the aggregated results include:

- `parser.py` which are helper functions to parse the raw files and turn them into per-run aggregated results. Because parsing each problem takes a significant amount of time, these aggregated results are then cached using `pickle` to the `all.cache` file (within the same folder where the results are stored).
- `metrics.py` is the script that aggregates metrics of multiple runs, possibly grouped by algorithm and particular configuration settings. The script is customized to group by the settings and algorithms presented in the paper, but can be adapted for any other groupings required. The aggregated results are then printed on screen, and also exported as a pickle object in the `results.p` file (in the `scripts` folder) for further processing (plotting).
- `plots.ipynb` is an *IPython notebook* used to plot the results (loaded from the `results.p` file) to `pdf` figures using matplotlib. To execute it, you must first start ipython notebook (just run `ipython notebook` within the scripts folder) and a browser window will open that allows you to play with the plotting settings. The resulting graphs will be stored in the `scripts/graphs` folder.
