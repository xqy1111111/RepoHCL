#ifndef CONFIG_H
#define CONFIG_H

#include <fstream>
#include <iostream>
#include <set>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <vector>

using BlockConfigsType = std::unordered_map<std::string, std::string>;

namespace strhelper {
// Note: have any ' ' in s
void SplitStr2Vec(const std::string &s, std::vector<std::string> &result,
                  const std::string delim);
std::string trim(const std::string &s);
}; // namespace strhelper

class IgnLibPathConfig {
private:
  std::vector<std::string> ignoreLibPaths;

public: /* helper function */
  explicit IgnLibPathConfig(){};
  IgnLibPathConfig(const BlockConfigsType &cfg);

  std::string GetRealPurePath(const std::string &path);

public: /* debugging, maybe useful? */
  friend std::ostream &operator<<(std::ostream &os, IgnLibPathConfig &c);
  operator bool() { return ignoreLibPaths.empty() == false; };

public: /* interface */
  bool isInIgnoreLibPaths(const std::string &path);
  std::vector<std::string> &getIgnoreLibPaths() { return ignoreLibPaths; };
};

class Config {
  std::unordered_map<std::string, BlockConfigsType> options;
  std::pair<std::string, std::string>
  parseOptionLine(const std::string &optionLine);

public:
  Config(const std::string &configFile);
  Config(const std::unordered_map<std::string, BlockConfigsType> passOptions);
  BlockConfigsType getOptionBlock(const std::string &blockName);
  friend std::ostream &operator<<(std::ostream &os, Config &c);
  std::unordered_map<std::string, BlockConfigsType> getAllOptionBlocks();
  IgnLibPathConfig parseIgnPaths(const std::string &blockName);

public:
  static bool IsBlockConfigTrue(BlockConfigsType &enable,
                                const std::string &target);
};

#endif
