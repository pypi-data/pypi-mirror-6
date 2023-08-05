/*jslint white: true, onevar: true, undef: true, nomen: true, eqeqeq: true, plusplus: true, bitwise: true, regexp: true, newcap: true, immed: true, strict: true */
/*global Workspace, alert, console, LayoutManagerFactory, Modules, setTimeout, Wirecloud */
"use strict";

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


var OpManagerFactory = (function () {

    // *********************************
    // SINGLETON INSTANCE
    // *********************************
    var instance = null,
        Singleton;

    function OpManager() {

        var loadEnvironment,
            onError;

        // ****************
        // CALLBACK METHODS
        // ****************

        loadEnvironment = function (transport) {
            var workspaces = JSON.parse(transport.responseText),
                workspace, state, i;

            for (i = 0; i < workspaces.length; i += 1) {
                workspace = workspaces[i];

                this.workspaceInstances[workspace.id] = workspace;
                if (!(workspace.creator in this.workspacesByUserAndName)) {
                    this.workspacesByUserAndName[workspace.creator] = {};
                }
                this.workspacesByUserAndName[workspace.creator][workspace.name] = workspace;
            }

            HistoryManager.init();
            state = HistoryManager.getCurrentState();
            this.changeActiveWorkspace(this.workspacesByUserAndName[state.workspace_creator][state.workspace_name]);
        };

        onError = function (transport, e) {
            alert("error en loadEnvironment");
        };


        // *********************************
        // PRIVATE VARIABLES AND FUNCTIONS
        // *********************************

        // ****************
        // PUBLIC METHODS
        // ****************
        OpManager.prototype.logIWidgetError = function (iwidget, msg, type) {
            console.log(msg);
        };

        OpManager.prototype.sendBufferedVars = function () {
            this.activeWorkspace.sendBufferedVars();
        };

        OpManager.prototype.changeActiveWorkspace = function (workspace) {
            var state;

            if (this.activeWorkspace != null) {
                this.activeWorkspace.unload();
            }

            state = {
                workspace_creator: workspace.creator,
                workspace_name: workspace.name,
                view: "workspace"
            };
            HistoryManager.pushState(state);

            this.loadCompleted = false;
            var workspaceUrl = Wirecloud.URLs.WORKSPACE_ENTRY.evaluate({'workspace_id': workspace.id});
            Wirecloud.io.makeRequest(workspaceUrl, {
                method: 'GET',
                requestHeaders: {'Accept': 'application/json'},
                onSuccess: function (response) {
                    var workspace_data = JSON.parse(response.responseText);
                    this.activeWorkspace = new Workspace(workspace_data);
                    this.activeWorkspace.contextManager.addCallback(function (updated_attributes) {
                        var workspace, old_name;

                        if ('name' in updated_attributes) {
                            workspace = this.workspaceInstances[this.activeWorkspace.id];
                            old_name = workspace.name;
                            delete this.workspacesByUserAndName[workspace.creator][old_name];

                            workspace.name = updated_attributes.name;
                            this.workspacesByUserAndName[workspace.creator][workspace.name] = workspace;
                        }
                    }.bind(this));
                    this.visibleLayer = 'tabs_container';
                    this.loadCompleted = true;
                }.bind(this)
            });
            this.showWidgetsMenuFromWorskspaceMenu();
        };

        OpManager.prototype.loadEnviroment = function () {
            LayoutManagerFactory.getInstance().resizeWrapper();
            // First, global modules must be loades (Showcase, Catalogue)
            // Showcase is the first!
            // When it finish, it will invoke continueLoadingGlobalModules method!

            Wirecloud.io.makeRequest(Wirecloud.URLs.PLATFORM_CONTEXT_COLLECTION, {
                method: 'GET',
                requestHeaders: {'Accept': 'application/json'},
                onSuccess: function (transport) {
                    OpManagerFactory.getInstance().contextManager = new Wirecloud.ContextManager(this, JSON.parse(transport.responseText));
                    OpManagerFactory.getInstance().continueLoadingGlobalModules(Modules.prototype.CONTEXT);
                }
            });
        };

        OpManager.prototype.showActiveWorkspace = function () {
            this.activeWorkspace.init();
        };

        OpManager.prototype.continueLoadingGlobalModules = function (module) {
            // Asynchronous load of modules
            // Each singleton module notifies OpManager it has finished loading!
            switch (module) {

            case Modules.prototype.CONTEXT:

                Wirecloud.io.makeRequest(Wirecloud.URLs.THEME_ENTRY.evaluate({name: this.contextManager.get('theme')}), {
                    method: 'GET',
                    requestHeaders: {'Accept': 'application/json'},
                    onSuccess: function (transport) {
                        Wirecloud.currentTheme = new Wirecloud.ui.Theme(JSON.parse(transport.responseText));
                        this.continueLoadingGlobalModules(Modules.prototype.THEME_MANAGER);
                    }.bind(this)
                });
                break;

            case Modules.prototype.THEME_MANAGER:

                Wirecloud.LocalCatalogue.reload({
                    onSuccess: function () {
                        this.continueLoadingGlobalModules(Modules.prototype.SHOWCASE);
                    }.bind(this),
                    onFailure: function () {
                        var msg = Wirecloud.GlobalLogManager.formatAndLog(gettext("Error retrieving available resources: %(errorMsg)s."), transport, e);
                        LayoutManagerFactory.getInstance().showMessageMenu(msg, Constants.Logging.ERROR_MSG);
                    }
                });
                break;
            case Modules.prototype.SHOWCASE:
                // All singleton modules has been loaded!
                // It's time for loading tabspace information!
                this.loadActiveWorkspace();
                break;
            }
        };

        OpManager.prototype.loadActiveWorkspace = function () {
            // Asynchronous load of modules
            // Each singleton module notifies OpManager it has finished loading!

            Wirecloud.io.makeRequest(Wirecloud.URLs.WORKSPACE_COLLECTION, {
                method: 'GET',
                requestHeaders: {'Accept': 'application/json'},
                onSuccess: loadEnvironment.bind(this),
                onFailure: onError,
                onException: onError
            });
        };

        //Operations on workspaces

        OpManager.prototype.workspaceExists = function (newName) {
            var workspaceId;
            for (workspaceId in this.workspaceInstances) {
                if (workspaceValues[i].workspaceState.name === newName) {
                    return true;
                }
            }
            return false;
        };


        OpManager.prototype.showDragboard = function (iWidgetId) {
            var dragboard = this.activeWorkspace.getIWidget(iWidgetId).dragboard;
            dragboard.paint(iWidgetId);
            this.visibleLayer = "dragboard";
        };

        OpManager.prototype.showWidgetsMenu = function () {
            this.alternatives.showAlternative(this.workspaceTabsAlternative);
            this.visibleLayer = "tabs_container";
            this.activeWorkspace.show();
        };

        OpManager.prototype.showWidgetsMenuFromWorskspaceMenu = function () {
            if (!this.loadCompleted) {
                setTimeout(function () {
                    OpManagerFactory.getInstance().showWidgetsMenuFromWorskspaceMenu();
                }, 100);
                return;
            }
            this.showActiveWorkspace(this.activeWorkspace);
            this.visibleLayer = "tabs_container";
        };

        OpManager.prototype.showWorkspaceMenu = function () {
            //generate the workspace list
            var workspaceId, workspace, workspaceEntry;

            this.workspaceListElement.innerHTML = '';
            for (workspaceId in this.workspaceInstances) {
                workspace = this.workspaceInstances[workspaceId];
                workspaceEntry = document.createElement('li');
                workspaceEntry.textContent = workspace.name;
                if (workspace === this.activeWorkspace) {
                    workspaceEntry.setAttribute('class', 'selected');
                    workspaceEntry.addEventListener('click', this.showWidgetsMenuFromWorskspaceMenu.bind(this), false);
                } else {
                    workspaceEntry.addEventListener('click', this.changeActiveWorkspace.bind(this, workspace), false);
                }
                this.workspaceListElement.appendChild(workspaceEntry);
            }
            //html += "<li class='bold'><a href='javascript:CatalogueFactory.getInstance().loadCatalogue()' class='arrow'>Add Mobile Mashup</a></li>";

            this.alternatives.showAlternative(this.workspaceListAlternative);
            this.visibleLayer = "workspace_menu";
        };

        // Singleton modules
        this.loadCompleted = false;
        this.visibleLayer = null;

        // Variables for controlling the collection of wiring and dragboard instances of a user
        this.workspaceInstances = {};
        this.workspacesByUserAndName = {};
        this.activeWorkspace = null;

        // workspace menu element
        this.workspaceMenuElement = document.getElementById('workspace_menu');
        this.workspaceListElement = document.getElementById('workspace_list');
        this.alternatives = new StyledElements.StyledAlternatives();
        this.workspaceListAlternative = this.alternatives.createAlternative();
        this.workspaceListAlternative.appendChild(this.workspaceMenuElement);

        this.workspaceTabsAlternative = this.alternatives.createAlternative({'class': 'tabs_container'});

        this.iwidgetViewAlternative = this.alternatives.createAlternative();
        this.globalDragboard = new MobileDragboard();
        this.iwidgetViewAlternative.appendChild(this.globalDragboard);
        this.alternatives.addEventListener('preTransition', function (alternatives, out_alternative, in_alternative) {
            alternatives.repaint();
            in_alternative.repaint();
        });
        this.iwidgetViewAlternative.addEventListener('hide', this.sendBufferedVars.bind(this));

        this.alternatives.insertInto(document.body);
    }

    // *********************************
    // SINGLETON GET INSTANCE
    // *********************************
    Singleton = function () {
        this.getInstance = function () {
            if (instance === null || instance === undefined) {
                instance = new OpManager();
            }
            return instance;
        };
    };

    return new Singleton();

}());
