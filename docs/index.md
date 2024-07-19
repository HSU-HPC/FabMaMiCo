# Welcome to FabMaMiCo

This is the documentation for the FabMaMiCo project.

## Introduction

**FabMaMiCo** is a plugin for [FabSim3](https://www.github.com/djgroen/FabSim3).

**FabSim3** is a workflow automation tool for automating complex tasks on remote high-performance computing (HPC) resources, like submitting jobs, transferring files, and executing commands on remote machines.

**MaMiCo** is a framework for hybrid fluid flow simulations, coupling fluid dynamics and molecular dynamics codes.
The framework is designed to be highly flexible and extensible, and to support incoprorated and external solvers for both the MD and CFD simulations.
Its setup is thus highly complex and requires a lot of manual work, which in its nature is both error-prone and time-consuming.

FabMaMiCo aims to automate the setup and execution of MaMiCo simulations.
As a plugin for FabSim3, it builds on top of FabSim3's functionality to automate the setup and execution of MaMiCo simulations.

## Requirements

- Python 3.6 or higher
- Access to a remote HPC resource (via SSH)