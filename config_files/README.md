# config_files

This folder contains several configurations.

- The `simA`, `simB`, `simC` directories contain configurations for exemplary task executions.
- The `study_x` directories contain configurations for the case studies.


## simX
Each configuration contains a `README.md`-file with detailed information about the configuration.
They present exemplary configurations for MaMiCo simulations, including sequential, parallel execution, replicas, and different scenarios.


## Case Study 1






Amartya: laufzeitvariabilität analysieren zwischen Clustern, stabil vs. hohe Varianz (hardware&software), ls1, one-way-coupling couette
    okay: now include ls1

Piet: LB, Couette, viele MD, [evtl filter für glatte Daten], 30x laufen lassen, Random-Seed untersuchen, two-way-coupling
    missing piets filter

Piet: filter, h², mit verschiedenen Szenarien, oscillating for POD-Analyse, NLM-Analyse, in paper nur testschachfeld, [vortex]
    missing piets filter











---------------------------------------


channelheight, 50x50x50 cube
fluid ist immer mit vel 0 initialisiert
wall-init-cycles: 0 md steps before
wall-velocity: boundary-condition, klein: hohes rauschen, groß: kann zu problemen führen, MD kann crashen, bei 1.5 zB, Usher probleme, step verkleinern, 2D nicht benutzbar

50 ist niedrig, nur daran interessiert, ob es funktioniert (für Laufzeittest sinnvoll, nicht für Strömungsdaten, oder pb Simulation pber längere zeit stabil, 2000-3000)

csv output in sendMDmacro => immer yes, mpi Kommunikation mitmessen, nie auf "no" schalten
evtl filter-init-cycles für 3. Case-Study (manchmal etwas tun, before couette startup), nur wenn two-way-coupling=yes, nur analyse von couette-startup
write-csv-every-timestep: bei sendMD2macro, feature von couette, timestep: COUPLING CYCLE (nicht md, cfd timestep)
compute-snr: signal to noise ratio (entweder selber mit python script basteln oder verwenden, aber source code checken)

equilibration-steps: 10.000 oder checkpoint verwenden!, Checkpoint auf bestimmte Domain & Boundary conditions bezogen (2. Case-Study)
number-md-simulations: 4: processes
particle-insertion: dann reflecting boundary

number of timesteps: # MD steps per coupling cycle

init-from-sequential-checkpoint, init-from-checkpoint