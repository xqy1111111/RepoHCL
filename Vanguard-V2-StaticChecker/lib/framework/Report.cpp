#include "framework/Report.h"

void ReportSpace::Defect::addDesc(const std::string &desc) {
  additionalInfo.push_back(desc);
}

std::vector<std::string> &ReportSpace::Defect::getDesc() {
  return additionalInfo;
}

void ReportSpace::Defect::dump(const std::string &indentation0) {
  std::string indentation = "  ";
  std::cout << indentation0 + "{" << std::endl;

  std::string indentation1 = indentation0 + indentation;
  std::cout << indentation1 + "\"DefectName\": ";
  switch (name) {
  case DefectName::MemoryLeak:
    std::cout << "\"MemoryLeak\"," << std::endl;
    break;
  case DefectName::MbufMemoryLeak:
    std::cout << "\"MbufMemoryLeak\"," << std::endl;
    break;
  case DefectName::DoubleFree:
    std::cout << "\"DoubleFree\"," << std::endl;
    break;
  case DefectName::MbufDoubleFree:
    std::cout << "\"MbufDoubleFree\"," << std::endl;
    break;
  case DefectName::UninitializedStructureMember:
    std::cout << "\"UninitializedStructureMember\"," << std::endl;
    break;
  case DefectName::MemoryRewrite:
    std::cout << "\"MemoryRewrite\"," << std::endl;
    break;
  case DefectName::RedundantRullCheck:
    std::cout << "\"RedundantRullCheck\"," << std::endl;
    break;
  case DefectName::RedundantFunctionCallInLoop:
    std::cout << "\"RedundantFunctionCallInLoop\"," << std::endl;
    break;
  case DefectName::ExpensiveFunctionCall:
    std::cout << "\"ExpensiveFunctionCall\"," << std::endl;
    break;
  case DefectName::ReduceLock:
    std::cout << "\"ReduceLock\"," << std::endl;
    break;
  case DefectName::ProcessSwitchingFrequently:
    std::cout << "\"ProcessSwitchingFrequently\"," << std::endl;
    break;
  case DefectName::InstructionLayout:
    std::cout << "\"InstructionLayout\"," << std::endl;
    break;
  case DefectName::DataLayout:
    std::cout << "\"DataLayout\"," << std::endl;
    break;
  case DefectName::FakeCachelineShare:
    std::cout << "\"FakeCachelineShare\"," << std::endl;
    break;
  case DefectName::AlignCacheline:
    std::cout << "\"AlignCacheline\"," << std::endl;
    break;
  case DefectName::AddLikelyOrUnlikelyToBranch:
    std::cout << "\"AddLikelyOrUnlikelyToBranch\"," << std::endl;
    break;
  case DefectName::ExpensiveOperation:
    std::cout << "\"ExpensiveOperation\"," << std::endl;
    break;
  case DefectName::CPUOutOfOrderExecution:
    std::cout << "\"CPUOutOfOrderExecution\"," << std::endl;
    break;
  case DefectName::SlowMemoryOperation:
    std::cout << "\"SlowMemoryOperation\"," << std::endl;
    break;
  case DefectName::HugeMemory:
    std::cout << "\"HugeMemory\"," << std::endl;
    break;
  default:
    std::cout << "," << std::endl;
    break;
  }

  std::cout << indentation1 + "\"DefectType\": ";
  switch (type) {
  case DefectType::Error:
    std::cout << "\"Error\"," << std::endl;
    break;
  case DefectType::Warning:
    std::cout << "\"Warning\"," << std::endl;
    break;
  default:
    std::cout << "," << std::endl;
    break;
  }

  std::cout << indentation1 + "\"FilePath\": \"" << filePath << "\","
            << std::endl;
  std::cout << indentation1 + "\"Line\": " << line << "," << std::endl;
  std::cout << indentation1 + "\"Column\": " << column << "," << std::endl;
  std::cout << indentation1 + "\"VariableName\": \"" << variableName << "\","
            << std::endl;
  std::cout << indentation1 + "\"AdditionalInfo\": [" << std::endl;

  std::string indentation2 = indentation1 + indentation;
  for (std::vector<std::string>::iterator it = additionalInfo.begin(),
                                          it_end = additionalInfo.end();
       it != it_end;) {
    std::cout << indentation2 << "\"" << (*it) << "\"";
    if (++it == it_end)
      std::cout << std::endl;
    else
      std::cout << "," << std::endl;
  }

  std::cout << indentation1 + "]" << std::endl;

  std::cout << indentation0 + "}";
}

void ReportSpace::Defect::dumpToFile(const std::string &indentation0,
                                     std::ofstream &process_file) {
  std::string indentation = "  ";
  process_file << indentation0 + "{" << std::endl;

  std::string indentation1 = indentation0 + indentation;
  process_file << indentation1 + "\"DefectName\": ";
  switch (name) {
  case DefectName::MemoryLeak:
    process_file << "\"MemoryLeak\"," << std::endl;
    break;
  case DefectName::MbufMemoryLeak:
    process_file << "\"MbufMemoryLeak\"," << std::endl;
    break;
  case DefectName::DoubleFree:
    process_file << "\"DoubleFree\"," << std::endl;
    break;
  case DefectName::MbufDoubleFree:
    process_file << "\"MbufDoubleFree\"," << std::endl;
    break;
  case DefectName::UninitializedStructureMember:
    process_file << "\"UninitializedStructureMember\"," << std::endl;
    break;
  case DefectName::MemoryRewrite:
    process_file << "\"MemoryRewrite\"," << std::endl;
    break;
  case DefectName::RedundantRullCheck:
    process_file << "\"RedundantRullCheck\"," << std::endl;
    break;
  case DefectName::RedundantFunctionCallInLoop:
    process_file << "\"RedundantOperationInLoop\"," << std::endl;
    break;
  case DefectName::ExpensiveFunctionCall:
    process_file << "\"ExpensiveFunctionCall\"," << std::endl;
    break;
  case DefectName::ReduceLock:
    process_file << "\"ReduceLock\"," << std::endl;
    break;
  case DefectName::ProcessSwitchingFrequently:
    process_file << "\"ProcessSwitchingFrequently\"," << std::endl;
    break;
  case DefectName::InstructionLayout:
    process_file << "\"InstructionLayout\"," << std::endl;
    break;
  case DefectName::DataLayout:
    process_file << "\"DataLayout\"," << std::endl;
    break;
  case DefectName::FakeCachelineShare:
    process_file << "\"FakeCachelineShare\"," << std::endl;
    break;
  case DefectName::AlignCacheline:
    process_file << "\"AlignCacheline\"," << std::endl;
    break;
  case DefectName::AddLikelyOrUnlikelyToBranch:
    process_file << "\"AddLikelyOrUnlikelyToBranch\"," << std::endl;
    break;
  case DefectName::ExpensiveOperation:
    process_file << "\"ExpensiveOperation\"," << std::endl;
    break;
  case DefectName::CPUOutOfOrderExecution:
    process_file << "\"CPUOutOfOrderExecution\"," << std::endl;
    break;
  case DefectName::SlowMemoryOperation:
    process_file << "\"SlowMemoryOperation\"," << std::endl;
    break;
  case DefectName::HugeMemory:
    process_file << "\"HugeMemory\"," << std::endl;
    break;
  default:
    process_file << "," << std::endl;
    break;
  }

  process_file << indentation1 + "\"DefectType\": ";
  switch (type) {
  case DefectType::Error:
    process_file << "\"Error\"," << std::endl;
    break;
  case DefectType::Warning:
    process_file << "\"Warning\"," << std::endl;
    break;
  default:
    process_file << "," << std::endl;
    break;
  }

  process_file << indentation1 + "\"FilePath\": \"" << filePath << "\","
               << std::endl;
  process_file << indentation1 + "\"Line\": " << line << "," << std::endl;
  process_file << indentation1 + "\"Column\": " << column << "," << std::endl;
  process_file << indentation1 + "\"VariableName\": \"" << variableName << "\","
               << std::endl;
  process_file << indentation1 + "\"AdditionalInfo\": [" << std::endl;

  std::string indentation2 = indentation1 + indentation;
  for (std::vector<std::string>::iterator it = additionalInfo.begin(),
                                          it_end = additionalInfo.end();
       it != it_end;) {
    process_file << indentation2 << "\"" << (*it) << "\"";
    if (++it == it_end)
      process_file << std::endl;
    else
      process_file << "," << std::endl;
  }

  process_file << indentation1 + "]" << std::endl;

  process_file << indentation0 + "}";
}

void ReportSpace::Report::addToReport(Defect *d) { defects.push_back(d); }

void ReportSpace::Report::writeJsonToFile() {}

void ReportSpace::Report::dump() {
  std::string indentation = "  ";
  std::string indentation0 = "";
  std::cout << indentation0 + "{" << std::endl;

  std::string indentation1 = indentation0 + indentation;
  std::cout << indentation1 + "\"TotalDefects\": " << defects.size() << ","
            << std::endl;
  std::cout << indentation1 + "\"Defects\": [" << std::endl;

  for (std::vector<Defect *>::iterator it = defects.begin(),
                                       it_end = defects.end();
       it != it_end;) {
    (*it)->dump(indentation1 + indentation);
    if (++it == it_end)
      std::cout << std::endl;
    else
      std::cout << "," << std::endl;
  }
  std::cout << indentation1 + "]" << std::endl;

  std::cout << indentation0 + "}" << std::endl;

  dumpToFile();
}

void ReportSpace::Report::dumpToFile() {
  std::ofstream process_file("report.json");
  if (!process_file.is_open()) {
    std::cerr << "can't open time.txt\n";
    return;
  }
  std::string indentation = "  ";
  std::string indentation0 = "";
  process_file << indentation0 + "{" << std::endl;

  std::string indentation1 = indentation0 + indentation;
  process_file << indentation1 + "\"TotalDefects\": " << defects.size() << ","
               << std::endl;
  process_file << indentation1 + "\"Defects\": [" << std::endl;

  for (std::vector<Defect *>::iterator it = defects.begin(),
                                       it_end = defects.end();
       it != it_end;) {
    (*it)->dumpToFile(indentation1 + indentation, process_file);
    if (++it == it_end)
      process_file << std::endl;
    else
      process_file << "," << std::endl;
  }
  process_file << indentation1 + "]" << std::endl;

  process_file << indentation0 + "}" << std::endl;
}

ReportSpace::Report::~Report() {
  for (Defect *d : defects) {
    delete d;
    d = nullptr;
  }
  defects.clear();
}
