// This file is part of MorphoDiTa.
//
// Copyright 2013 by Institute of Formal and Applied Linguistics, Faculty of
// Mathematics and Physics, Charles University in Prague, Czech Republic.
//
// MorphoDiTa is free software: you can redistribute it and/or modify
// it under the terms of the GNU Lesser General Public License as
// published by the Free Software Foundation, either version 3 of
// the License, or (at your option) any later version.
//
// MorphoDiTa is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Lesser General Public License for more details.
//
// You should have received a copy of the GNU Lesser General Public License
// along with MorphoDiTa.  If not, see <http://www.gnu.org/licenses/>.

#pragma once

#include "../common.h"

namespace ufal {
namespace morphodita {

// Read line and strip '\n'.
bool getline(FILE *f, string& line);

// Read a paragraph separated by an empty line. All '\n' are left intact.
bool getpara(FILE* f, string& para);

// Split given text on the separator character.
void split(const string& text, char sep, vector<string>& tokens);

} // namespace morphodita
} // namespace ufal
