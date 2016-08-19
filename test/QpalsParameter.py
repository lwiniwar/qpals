"""
/***************************************************************************
Name			 	 : qpalsModuleBase
Description          : base class and functions for all modules
Date                 : 2016-05-21
copyright            : (C) 2016 by Lukas Winiwarter/TU Wien
email                : lukas.winiwarter@tuwien.ac.at
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 """

class QpalsParameter:

    changed = False
    use4proj = None
    field = None
    browse = None
    icon = None

    def __init__(self, name, val, choices, type, opt, desc, longdesc):
        self.name = name
        self.choices = choices
        self.type = type
        self.val = val
        self.opt = opt
        self.desc = desc
        self.longdesc = longdesc