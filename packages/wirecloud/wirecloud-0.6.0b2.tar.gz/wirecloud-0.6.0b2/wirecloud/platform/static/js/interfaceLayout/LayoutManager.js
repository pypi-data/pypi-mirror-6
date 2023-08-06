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


var LayoutManagerFactory = function () {

    // *********************************
    // SINGLETON INSTANCE
    // *********************************
    var instance = null;

    // *********************************
    // PRIVATE CONSTANTS
    // *********************************

    function LayoutManager () {
        // *********************************
        // PRIVATE VARIABLES
        // *********************************

        this.mainLayout = new StyledElements.BorderLayout();
        this.mainLayout.getNorthContainer().appendChild(document.getElementById('wirecloud_header'));

        this.alternatives = new StyledElements.StyledAlternatives();
        this.mainLayout.getCenterContainer().appendChild(this.alternatives);
        this.mainLayout.insertInto(document.body);

        /* TODO| FIXME */
        this.header = new Wirecloud.ui.WirecloudHeader(this);
        this.alternatives.addEventListener('postTransition', function (alternatives, old_alternative, new_alternative) {
            Wirecloud.HistoryManager.pushState(new_alternative.buildStateData());
            this.header._notifyViewChange(new_alternative);
        }.bind(this));
        this.viewsByName = {
            'workspace': this.alternatives.createAlternative({'alternative_constructor': WorkspaceView}),
            'wiring': this.alternatives.createAlternative({'alternative_constructor': Wirecloud.ui.WiringEditor}),
            'marketplace': this.alternatives.createAlternative({'alternative_constructor': MarketplaceView})
        };
        this.header._notifyViewChange(this.viewsByName['workspace']);

        // Container managed by LayOutManager: {showcase_tab}
        // Remaining containers managed by Workspaces!!
        this._clickCallback = this._clickCallback.bind(this);
        this.timeout = null;
        document.getElementById("loading-window").addEventListener('click', this._clickCallback, true);

        // Menu Layer
        this.currentMenu = null;                                // current menu (either dropdown or window)
        this.coverLayerElement = document.getElementById('menu_layer');               // disabling background layer
        this.coverLayerElement.className = 'disabled_background fade';

        this.menus = new Array();

        // Listen to resize events
        window.addEventListener("resize", this.resizeWrapper.bind(this), true);
    }

        // ***************
        // PUBLIC METHODS
        // ****************


        LayoutManager.prototype._updateTaskProgress = function() {
            var msg, subtaskpercentage, taskpercentage;

            subtaskpercentage = Math.round((this.currentStep * 100) / this.totalSteps);
            if (subtaskpercentage < 0) {
                subtaskpercentage = 0;
            } else if (subtaskpercentage > 100) {
                subtaskpercentage = 100;
            }

            taskpercentage = (this.currentSubTask * 100) / this.totalSubTasks;
            taskpercentage += subtaskpercentage * (1 / this.totalSubTasks);
            taskpercentage = Math.round(taskpercentage);
            if (taskpercentage < 0) {
                taskpercentage = 0;
            } else if (taskpercentage > 100) {
                subtaskpercentage = 100;
            }

            msg = gettext("%(task)s %(percentage)s%");
            msg = interpolate(msg, {task: this.task, percentage: taskpercentage}, true);
            document.getElementById("loading-task-title").textContent = msg;

            if (this.subTask != "") {
                msg = gettext("%(subTask)s: %(percentage)s%");
            } else {
                msg = "%(subTask)s";
            }

            msg = interpolate(msg, {subTask: this.subTask, percentage: subtaskpercentage}, true);
            document.getElementById("loading-subtask-title").textContent = msg;
        }

        LayoutManager.prototype._startComplexTask = function(task, subtasks) {
            this.task = task ? task : "";
            this.currentSubTask = -2;
            this.totalSubTasks = subtasks != undefined ? subtasks : 1;
            this.logSubTask("");
            document.getElementById("loading-window").classList.remove("disabled");
        }

        LayoutManager.prototype.logSubTask = function(msg, totalSteps) {
            this.subTask = msg ? msg : "";

            if (msg) {
                Wirecloud.GlobalLogManager.log(msg, Constants.Logging.INFO_MSG);
            }

            this.currentSubTask++;
            if (this.currentSubTask >= this.totalSubTasks)
                this.totalSubTasks = this.currentSubTask + 1;

            this.currentStep = 0;
            if (arguments.length == 2)
                this.totalSteps = totalSteps;
            else
                this.totalSteps = 1;

            this._updateTaskProgress();
        }

        LayoutManager.prototype.logStep = function(msg, totalSteps) {
            //document.getElementById("loading-step-title").textContent = msg ? msg : "";
            this.currentStep++;
            if (this.currentStep > this.totalSteps)
                this.totalSteps = this.currentStep + 1;

            if (arguments.length == 2)
                this.totalSteps = totalSteps;

            this._updateTaskProgress();
        }

        LayoutManager.prototype._hideProgressIndicator = function () {
            var loadingElement = document.getElementById("loading-window");
            var loadingMessage = document.getElementById("loading-message");

            loadingElement.classList.add('disabled');
            loadingElement.classList.remove('fadding');
            loadingMessage.style.opacity = '1';

            if (this.timeout !== null) {
                clearTimeout(this.timeout);
                this.timeout = null;
            }
        };

        LayoutManager.prototype._clickCallback = function (event) {
            event = event || window.event;

            if (document.getElementById("loading-window").classList.contains("fadding")) {
                this._hideProgressIndicator();
            }
            if (event.stopPropagation) {
                event.stopPropagation();
            } else {
                event.cancelBubble = true;
            }
        };

        LayoutManager.prototype._notifyPlatformReady = function () {
            var loadingElement = document.getElementById("loading-window");
            loadingElement.classList.add("fadding");

            var loadingMessage = document.getElementById("loading-message");
            var step = 0;
            var layoutManager = this;
            function fadder() {
                ++step;
                if (step < 80) {
                    loadingMessage.style.opacity = "" + (1 - (step * 0.025));
                    layoutManager.timeout = setTimeout(fadder, 50);
                } else {
                    layoutManager._hideProgressIndicator();
                }
            }
            if (layoutManager.timeout !== null) {
                clearTimeout(layoutManager.timeout);
            }
            layoutManager.timeout = setTimeout(fadder, 50);
        }

        LayoutManager.prototype.resizeWrapper = function () {
            this.mainLayout.repaint();

            // Recalculate menu positions
            if (this.currentMenu) {
                this.currentMenu.calculatePosition();
            }
        }

        /****VIEW OPERATIONS****/
        LayoutManager.prototype.changeCurrentView = function(newView) {
            this.alternatives.showAlternative(this.viewsByName[newView]);
        };

        /*
         * Handler for changes in the hash to navigate to other areas
         */
        LayoutManager.prototype.onHashChange = function(state) {
            var tab_id, tab, nextWorkspace, opManager, dragboard, alert_msg;

            opManager = OpManagerFactory.getInstance();

            nextWorkspace = opManager.workspacesByUserAndName[state.workspace_creator][state.workspace_name];
            if (nextWorkspace == null) {
                if (Wirecloud.activeWorkspace != null) {
                    Wirecloud.activeWorkspace.unload();
                    Wirecloud.activeWorkspace = null;
                }
                alert_msg = document.createElement('div');
                alert_msg.className = 'alert alert-info';
                alert_msg.textContent = gettext('The requested workspace is no longer available (it was deleted).');;
                LayoutManagerFactory.getInstance().viewsByName['workspace'].clear();
                LayoutManagerFactory.getInstance().viewsByName['workspace'].appendChild(alert_msg);
                this.header.refresh();
            } else if (Wirecloud.activeWorkspace == null || (nextWorkspace.id !== Wirecloud.activeWorkspace.id)) {
                Wirecloud.changeActiveWorkspace(nextWorkspace, state.tab);
            }

            if (state.view !== this.alternatives.getCurrentAlternative().view_name) {
                this.alternatives.showAlternative(this.viewsByName[state.view]);
            }
        };

        LayoutManager.prototype.showUnclickableCover = function() {
            this.coverLayerElement.style.display = "block";
            setTimeout(function () {
                this.coverLayerElement.classList.add('in');
            }.bind(this), 0);
        };

        /**
         * @private
         * Only to be used by WindowMenu.
         */
        LayoutManager.prototype._showWindowMenu = function (window_menu) {
            if (!(window_menu instanceof Wirecloud.ui.WindowMenu)) {
                throw TypeError('window_menu must be a WindowMenu instance');
            }

            if (this.currentMenu != null) {
                // only if the layer is displayed.
                this.hideCover();
            }
            this.showUnclickableCover();
            this.currentMenu = window_menu;
        };

        /**
         * Shows the message window menu using the specified text. By default,
         * it will be interpreted as an information message, but you can use the
         * type param to change this behaviour.
         *
         * @param {String} msg Text of the message to show
         * @param {Constants.Logging} type Optional parameter to change the
         *        message type. (default value: Constants.Logging.INFO_MSG)
         */
        LayoutManager.prototype.showMessageMenu = function(msg, type) {
            var menu;
            if (!this.menus['messageMenu']) {
                this.menus['messageMenu'] = new Wirecloud.ui.MessageWindowMenu(null);
            }
            menu = this.menus['messageMenu'];

            type = type ? type : Constants.Logging.INFO_MSG;
            menu.setMsg(msg);
            menu.setType(type);
            // TODO: this.currentMenu???
            menu.show(this.currentMenu);
        }

        //hides the disabling layer and so, the current menu
        LayoutManager.prototype.hideCover = function() {
            if (this.currentMenu) {
                this.currentMenu.hide();
            }
            this.currentMenu = null;
            this.coverLayerElement.classList.remove('in');
            this.coverLayerElement.style.display = "none";
        }

    // *********************************
    // SINGLETON GET INSTANCE
    // *********************************
    return new function() {
    this.getInstance = function() {
        if (instance == null) {
            instance = new LayoutManager();
        }
        return instance;
        }
    }
}();
