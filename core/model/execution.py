"""
Cymulate's Execution Model
"""
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class InputArgument:
    _id: str
    name: str
    description: str
    type: str
    default: list
    takesInputFromSon: bool
    mutable: bool
    encrypted: bool
    uuid: str
    inputOptions: list


@dataclass
class Dependency:
    description: str
    prereqCommand: str
    getPrereqCommand: str
    dependencyExecutorName: str
    enabled: bool
    uuid: str
    _id: str


@dataclass
class Executor:
    name: str
    command: str
    elevationRequired: bool


@dataclass
class CleanupCommand:
    executorName: str
    command: str
    enabled: bool
    uuid: str
    _id: str


@dataclass
class OutputParser:
    suitableInputArguments: list
    description: str
    executorName: str
    command: str
    pipe: bool
    enabled: bool
    uuid: str
    _id: str


@dataclass
class SuccessIndicator:
    successIndicatorExecutor: str
    successIndicatorCommand: str
    enabled: bool
    description: str
    pipe: bool
    uuid: str
    _id: str


@dataclass
class Execution:
    _id: str
    public: bool
    visible: bool
    name: str
    displayName: str
    supportedPlatforms: list
    os: list
    description: str
    techniques: list
    tactics: list
    inputArguments: List[InputArgument]
    dependencies: List[Dependency]
    executor: Executor
    cleanupCommands: List[CleanupCommand]
    outputParsers: List[OutputParser]
    successIndicators: List[SuccessIndicator]
    iocs: Optional[list]
    tags: Optional[list]
    dataSources: Optional[list]
    cves: Optional[list]
    timeout: Optional[int]
    author: Optional[str]
    keywords: Optional[list]
    date: Optional[str]
    # not using __v because it has problem with instance private variable -> _Execution__v
    # __v: int
    nistTechniques: Optional[list]
    displayDate: Optional[str]

