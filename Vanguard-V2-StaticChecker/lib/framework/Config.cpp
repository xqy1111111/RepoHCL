#include "framework/Config.h"

#include <deque>
#include <llvm/Support/raw_ostream.h>

namespace strhelper {

std::string trim(const std::string &s) {
  std::string result = s;
  result.erase(0, result.find_first_not_of(" \t\r\n"));
  result.erase(result.find_last_not_of(" \t\r\n") + 1);
  return result;
}

void SplitStr2Vec(const std::string &s, std::vector<std::string> &result,
                  const std::string delim) {
  result.clear();

  if (s.empty()) {
    return;
  }

  size_t pos_start = 0, pos_end = s.find(delim), len = 0;

  // 1 substr, no delim
  if (pos_end == std::string::npos) {
    result.push_back(s);
    return;
  }

  // delimited args
  while (pos_end != std::string::npos) {
    len = pos_end - pos_start;
    result.push_back(s.substr(pos_start, len));
    pos_start = pos_end + delim.size();
    pos_end = s.find(delim, pos_start);
  }

  if (pos_start != s.size()) {
    result.push_back(s.substr(pos_start));
  }
}

}; // namespace strhelper

Config::Config(const std::unordered_map<std::string, BlockConfigsType> passOptions) {
    options = passOptions;
}

Config::Config(const std::string &configFile) {
  std::ifstream infile(configFile);
  std::string line;
  while (std::getline(infile, line)) {
    line = strhelper::trim(line);
    if (line == "") {
      continue;
    }
    BlockConfigsType oneBlockOption;
    std::string optionBlockName = line;
    std::getline(infile, line);
    line = strhelper::trim(line);
    if (line != "{") {
      std::cout << "config file format error\n";
      exit(1);
    }
    while (std::getline(infile, line)) {
      line = strhelper::trim(line);
      if (line == "") {
        continue;
      }
      if (line == "}") {
        options.insert(std::make_pair(optionBlockName, oneBlockOption));
        break;
      }
      auto parsedLine = parseOptionLine(line);
      oneBlockOption.insert(parsedLine);
    }
  }
}

std::pair<std::string, std::string>
Config::parseOptionLine(const std::string &optionLine) {
  int index = optionLine.find("=");
  std::string name = optionLine.substr(0, index);
  std::string value = optionLine.substr(index + 1);
  name = strhelper::trim(name);
  value = strhelper::trim(value);
  return std::make_pair(name, value);
}

BlockConfigsType Config::getOptionBlock(const std::string &blockName) {
  std::unordered_map<std::string, BlockConfigsType>::const_iterator got =
      options.find(blockName);
  if (got == options.end()) {
    std::cout << "[!] block name not found: " << blockName << "\n";
    exit(1);
  } else {
    return got->second;
  }
}

std::unordered_map<std::string, BlockConfigsType> Config::getAllOptionBlocks() {
  return options;
}

std::ostream &operator<<(std::ostream &os, Config &c) {
  for (auto block : c.getAllOptionBlocks()) {
    os << "block name: " << block.first << "\n";
    for (auto blockOpt : block.second) {
      os << "\t"
         << "option name = " << blockOpt.first << "\n";
      os << "\t"
         << "option value = " << blockOpt.second << "\n";
    }
  }
  return os;
}

bool Config::IsBlockConfigTrue(BlockConfigsType &enable,
                               const std::string &target) {
  BlockConfigsType::const_iterator got = enable.find(target);
  if (got == enable.end()) {
    return false;
  }
  if (got->second == "true")
    return true;
  else
    return false;
}

IgnLibPathConfig Config::parseIgnPaths(const std::string &blockName) {
  BlockConfigsType ptrConfig = getOptionBlock(blockName);
  return IgnLibPathConfig(ptrConfig);
}

/**************************
 * class IgnLibPathConfig *
 **************************/
IgnLibPathConfig::IgnLibPathConfig(const BlockConfigsType &cfg) {
  auto ilpCfg = cfg.find("ignoreLibPaths");
  if (ilpCfg != cfg.end()) {
    std::vector<std::string> tmpIgnPaths;
    strhelper::SplitStr2Vec(ilpCfg->second, tmpIgnPaths, ":");
    for (std::string &s : tmpIgnPaths) {
      std::string purepath = GetRealPurePath(s);
      if (!purepath.empty()) {
        // llvm::errs() << purepath << "\n";
        ignoreLibPaths.push_back(purepath);
      }
    }
  }
}

std::string IgnLibPathConfig::GetRealPurePath(const std::string &path) {
  std::vector<std::string> strvec;
  strhelper::SplitStr2Vec(path, strvec, "/");
  if (strvec.empty()) {
    llvm::errs() << "[!] Maybe Err(Empty String?)\n";
    return "";
  }
  if (!strvec[0].empty()) {
    llvm::errs() << "[!] Warning(Not absolute path)\n";
    return "";
  }

  std::deque<std::string> fakestack;
  // Note: start from idx = 1
  for (std::vector<std::string>::const_iterator it = strvec.begin() + 1,
                                                ed = strvec.end();
       it != ed; it++) {
    const std::string s = *it;
    if (s == ".") {
      continue;
    } else if (s == "..") {
      if (fakestack.empty()) {
        llvm::errs() << "[-] Err, Invail path(too many '..')\n";
        return "";
      } else {
        fakestack.pop_back();
      }
    } else {
      fakestack.push_back(s);
    }
  }

  std::string purepath;
  for (std::string &s : fakestack) {
    purepath += ('/' + s);
  }
  // realpath is '/'
  if (purepath.empty()) {
    purepath += '/';
  }
  // llvm::errs() << purepath << "\n";
  return purepath;
}

std::ostream &operator<<(std::ostream &os, IgnLibPathConfig &c) {
  os << "Ignore Lib Path:\n";
  if (c) {
    int cnt = 1;
    for (const std::string &p : c.getIgnoreLibPaths()) {
      os << "  " << cnt << ". " << p << "\n";
      cnt++;
    }
  } else {
    os << "  [Empty]\n";
  }
  return os;
}

bool IgnLibPathConfig::isInIgnoreLibPaths(const std::string &path) {
  std::string realpath = GetRealPurePath(path);
  for (std::string &libpath : ignoreLibPaths) {
    std::string::size_type idx = realpath.find(libpath);
    if (idx == 0) {
      return true;
    }
  }
  return false;
}
