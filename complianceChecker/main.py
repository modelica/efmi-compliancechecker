# Copyright (c) 2021, ESI ITI GmbH, Modelica Association and contributors
# 
# Licensed under the 3-Clause BSD license (the "License");
# you may not use this software except in compliance with
# the "License".
# 
# This software is not fully developed or tested.
# 
# THE SOFTWARE IS PROVIDED "as is", WITHOUT ANY WARRANTY
# of any kind, either express or implied, and the use is 
# completely at your own risk.
# 
# The software can be redistributed and/or modified under
# the terms of the "License".
# 
# See the "License" for the specific language governing
# permissions and limitations under the "License".

import ComplianceChecker
import sys

if __name__ == "__main__":
    #"D:\projects\Emphysis\eFMUs\M01_SimplePI.Tests.Controller_ExplEuler.fmu"
    ComplianceChecker.read_model_container(sys.argv[1])