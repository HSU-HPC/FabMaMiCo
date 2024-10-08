# Welcome to FabMaMiCo

This is the documentation for [FabMaMiCo](https://www.github.com/HSU-HPC/FabMaMiCo).

## Introduction

FabMaMiCo is a plugin for [FabSim3](https://www.github.com/djgroen/FabSim3), specifically designed for the [MaMiCo](https://www.github.com/HSU-HPC/MaMiCo) simulation framework.

**FabSim3** is a workflow automation tool for automating complex tasks on remote high-performance computing (HPC) resources.
It enables users to manage large-scale job submissions, file management and data analysis on remote machines.

**MaMiCo** is a framework for hybrid fluid flow simulations, coupling fluid dynamics and molecular dynamics solvers.
The framework is designed to be highly flexible and extensible, and to support incorporated and external solvers for both the MD and CFD simulation.
Its setup can thus be highly complex and it may require a lot of manual work, which in its nature is both error-prone and time-consuming.

**FabMaMiCo** aims to automate the setup and execution of MaMiCo simulations.
As a plugin for FabSim3, it builds on top of FabSim3's functionality.

It is key to understand that FabMaMiCo is a plugin that is ***designed to be adapted and extended by the user*** to fit their specific needs.
The plugin provides a set of tasks and configurations, but it is expected that users will need to adapt these to their specific use case.
Most of the tasks and configurations serve as examples.

## Requirements

- Python 3.6 or higher