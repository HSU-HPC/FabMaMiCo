# Welcome to FabMaMiCo

This is the documentation for [FabMaMiCo](https://www.github.com/HSU-HPC/FabMaMiCo).

## Introduction

FabMaMiCo is a plugin for [FabSim3](https://www.github.com/djgroen/FabSim3), specifically designed for the [MaMiCo](https://www.github.com/HSU-HPC/MaMiCo) simulation framework.

**FabSim3** is a workflow automation tool for automating complex tasks on remote high-performance computing (HPC) resources.
It enables users to manage large-scale job submissions, file management and data analysis on remote machines.

**MaMiCo** is a framework for hybrid fluid flow simulations, coupling fluid dynamics and molecular dynamics solvers.
The framework is designed to be highly flexible and extensible, and to support incorporated and external solvers for both the MD and CFD simulations.
Its setup can thus be highly complex and it may require a lot of manual work, which in its nature is both error-prone and time-consuming.

FabMaMiCo aims to automate the setup and execution of MaMiCo simulations.
As a plugin for FabSim3, it builds on top of FabSim3's functionality.

## Requirements

- Python 3.6 or higher
- Access to a remote HPC resource (via SSH)