#ifndef _REPORT_H
#define _REPORT_H
// #include "json/json.h"
#include <fstream>
#include <iostream>
#include <map>
#include <set>
#include <vector>

namespace ReportSpace
{

  enum DefectName
  {
    MemoryLeak,
    MbufMemoryLeak,
    DoubleFree,
    MbufDoubleFree,
    UninitializedStructureMember,
    MemoryRewrite,
    RedundantRullCheck,
    RedundantFunctionCallInLoop,
    ExpensiveFunctionCall,
    ReduceLock,
    ProcessSwitchingFrequently,
    InstructionLayout,
    DataLayout,
    FakeCachelineShare,
    AlignCacheline,
    AddLikelyOrUnlikelyToBranch,
    ExpensiveOperation,
    CPUOutOfOrderExecution,
    SlowMemoryOperation,
    HugeMemory
  };

  enum DefectType
  {
    Error,
    Warning
  };

  // class SingleDesc {
  // public:
  //   SingleDesc(std::string fileLoc, int l, std::string desc) :
  //   fileLoc(fileLoc), line(l), defectDesc(desc) {}
  // private:
  //   std::string fileLoc;
  //   int line;
  //   std::string defectDesc;
  // };

  class Defect
  {
  public:
    Defect(DefectName dn, DefectType dt, const std::string &fp, int l, int c,
           const std::string &vn)
        : name(dn), type(dt), filePath(fp), line(l), column(c), variableName(vn)
    {
    }

    void addDesc(const std::string &desc);
    std::vector<std::string> &getDesc();
    void dump(const std::string &indentation0);
    void dumpToFile(const std::string &indentation0, std::ofstream &process_file);

  private:
    DefectName name;
    DefectType type;
    std::string filePath;
    int line;
    int column;
    std::string variableName;
    std::vector<std::string> additionalInfo;
  };

  class Report
  {
  public:
    void addToReport(Defect *d);
    void writeJsonToFile();
    void dump();
    void dumpToFile();

    ~Report();

  private:
    std::vector<Defect *> defects;
  };

} // namespace ReportSpace

#endif