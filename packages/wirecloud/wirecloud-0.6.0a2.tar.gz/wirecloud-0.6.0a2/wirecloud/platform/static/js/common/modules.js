/* 
*     (C) Copyright 2008 Telefonica Investigacion y Desarrollo
*     S.A.Unipersonal (Telefonica I+D)
*
*     This file is part of Morfeo EzWeb Platform.
*
*     Morfeo EzWeb Platform is free software: you can redistribute it and/or modify
*     it under the terms of the GNU Affero General Public License as published by
*     the Free Software Foundation, either version 3 of the License, or
*     (at your option) any later version.
*
*     Morfeo EzWeb Platform is distributed in the hope that it will be useful,
*     but WITHOUT ANY WARRANTY; without even the implied warranty of
*     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*     GNU Affero General Public License for more details.
*
*     You should have received a copy of the GNU Affero General Public License
*     along with Morfeo EzWeb Platform.  If not, see <http://www.gnu.org/licenses/>.
*
*     Info about members and contributors of the MORFEO project
*     is available at
*
*     http://morfeo-project.org
 */


function Modules () {

}

Modules.prototype.CONTEXT = 5;
Modules.prototype.THEME_MANAGER = 3;
Modules.prototype.PLATFORM_PREFERENCES = 4;

// Singleton modules (valid for every Workspace)
Modules.prototype.SHOWCASE = 0;
Modules.prototype.CATALOGUE = 1;

//Each workspace loads one instance of VarManager and Wiring
// Each workspace loads loads n instaces of Drabgoard!
Modules.prototype.ACTIVE_WORKSPACE = 2;


