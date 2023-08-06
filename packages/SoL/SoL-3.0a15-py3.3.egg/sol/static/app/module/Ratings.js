//-*- coding: utf-8 -*-
//:Progetto:  SoL -- The ratings window
//:Creato:    gio 05 dic 2013 20:31:44 CET
//:Autore:    Lele Gaifax <lele@metapensiero.it>
//:Licenza:   GNU General Public License version 3 or later
//

/*jsl:declare Ext*/
/*jsl:declare _*/
/*jsl:declare MP*/
/*jsl:declare window*/
/*jsl:declare SoL*/

Ext.define('SoL.module.Ratings.Actions', {
    extend: 'MP.action.StoreAware',
    uses: [
        'Ext.Action',
        'MP.form.Panel',
        'MP.window.Notification'
    ],

    statics: {
        EDIT_RATING_ACTION: 'edit_rating',
        RECOMPUTE_RATING_ACTION: 'recompute_rating',
        DOWNLOAD_TOURNEYS_ACTION: 'download_tourneys',
        SHOW_TOURNEYS_ACTION: 'show_tourneys',
        SHOW_PLAYERS_ACTION: 'show_players'
    },

    initActions: function() {
        var me = this;
        var ids = me.statics();

        me.callParent();

        me.editRatingAction = me.addAction(new Ext.Action({
            itemId: ids.EDIT_RATING_ACTION,
            text: _('Modify'),
            tooltip: _('Edit selected rating.'),
            iconCls: 'edit-record-icon',
            disabled: true,
            needsOneSelectedRow: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0];
                me.showEditRatingWindow(record);
            }
        }));

        me.showTourneysAction = me.addAction(new Ext.Action({
            itemId: ids.SHOW_TOURNEYS_ACTION,
            text: _('Tourneys'),
            tooltip: _('Show tourneys related to the selected rating.'),
            iconCls: 'show-tourneys-icon',
            disabled: true,
            needsOneSelectedRow: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0];
                var idrating = record.get('idrating');
                var rating = record.get('description');
                var module = me.module.app.getModule('tourneys-win');
                module.createOrShowWindow('ratings', idrating, rating);
            }
        }));

        me.showPlayersAction = me.addAction(new Ext.Action({
            itemId: ids.SHOW_PLAYERS_ACTION,
            text: _('Players'),
            tooltip: _('Show rated players in the selected rating.'),
            iconCls: 'rated-players-icon',
            disabled: true,
            needsOneSelectedRow: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0];
                var idrating = record.get('idrating');
                var rating = record.get('description');
                var module = me.module.app.getModule('rated-players-win');
                module.createOrShowWindow(idrating, rating);
            }
        }));

        me.recomputeRatingAction = me.addAction(new Ext.Action({
            itemId: ids.RECOMPUTE_RATING_ACTION,
            text: _('Recompute'),
            tooltip: _('Recompute the selected rating from scratch.'),
            iconCls: 'recompute-rating-icon',
            disabled: true,
            needsOneSelectedRow: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0];
                var idrating = record.get('idrating');

                Ext.create("MP.window.Notification", {
                    position: 'br',
                    html: _('Recomputing...'),
                    title: _('Please wait'),
                    iconCls: 'waiting-icon'
                }).show();

                Ext.Ajax.request({
                    url: '/bio/recomputeRating',
                    params: { idrating: idrating },
                    success: function(response) {
                        var result = Ext.decode(response.responseText);

                        if(result.success) {
                            var store = me.component.store;

                            Ext.create("MP.window.Notification", {
                                position: 'br',
                                html: result.message,
                                title: _('Done'),
                                iconCls: 'done-icon'
                            }).show();

                            store.loadPage(store.currentPage);
                        } else {
                            Ext.create("MP.window.Notification", {
                                position: 'br',
                                html: result.message,
                                title: _('Error'),
                                iconCls: 'alert-icon'
                            }).show();
                        }
                    },
                    failure: function(response) {
                        Ext.create("MP.window.Notification", {
                            position: 'br',
                            html: response.responseText,
                            title: _('Error'),
                            iconCls: 'alert-icon'
                        }).show();
                    }
                });
            }
        }));

        me.downloadTourneysAction = me.addAction(new Ext.Action({
            itemId: ids.DOWNLOAD_TOURNEYS_ACTION,
            text: _('Download'),
            tooltip: _('Download all tourneys related to this rating.'),
            iconCls: 'download-icon',
            disabled: true,
            needsOneSelectedRow: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0];
                var idrating = record.get('idrating');
                var url = '/bio/dump?idrating=' + idrating;
                window.open(url, "_blank");
            }
        }));
    },

    attachActions: function() {
        var me = this;

        me.callParent();

        var tbar = me.component.child('#ttoolbar');

        tbar.add(2, ' ',
                 me.editRatingAction,
                 me.showTourneysAction,
                 me.showPlayersAction,
                 me.recomputeRatingAction,
                 me.downloadTourneysAction
        );

        me.component.on({
            itemdblclick: function() {
                me.editRatingAction.execute();
            }
        });
        me.component.store.on({
            add: function(store, records) {
                //jsl:unused store
                var record = records[0];
                me.showEditRatingWindow(record);
            }
        });
    },

    shouldDisableAction: function(act) {
        var me = this;
        var disable = me.component.shouldDisableAction(act);
        var statics = me.statics();

        if(!disable) {
            switch(act.itemId) {
                case statics.RECOMPUTE_RATING_ACTION:
                case statics.SHOW_TOURNEYS_ACTION:
                case statics.EDIT_RATING_ACTION:
                    // Disable pointless actions on historical ratings
                    if(me.component.getSelectionModel().getSelection()[0].get('level') == '0')
                        disable = true;
                    break;

                default:
                    break;
            }
        }
        return disable;
    },

    showEditRatingWindow: function(record) {
        var me = this;
        var desktop = me.module.app.getDesktop();
        var win = desktop.getWindow('edit-rating-win');
        var currentuser = me.module.app.user;
        var canchange = currentuser.is_admin;

        // If the window is already present, destroy and recreate it,
        // to reapply configuration and filters
        if(win) {
            win.destroy();
        }

        var metadata = me.module.config.metadata;
        var size = desktop.getReasonableWindowSize(600, 420);
        var editors = metadata.editors({
            '*': { editor: MP.form.Panel.getDefaultEditorSettingsFunction() },
            tau: { editor: { disabled: !canchange } },
            default_rate: { editor: { disabled: !canchange } },
            default_deviation: { editor: { disabled: !canchange } },
            default_volatility: { editor: { disabled: !canchange } }
        });

        // Remove the level 0, which cannot be assigned explicitly
        editors.level.store.splice(0, 1);

        var form = Ext.create('MP.form.Panel', {
            autoScroll: true,
            fieldDefaults: {
                labelWidth: 150,
                margin: '15 0 0 20'
            },
            items: [
                editors.description,
                editors.level,
                editors.inherit,
                editors.tau,
                editors.default_rate,
                editors.default_deviation,
                editors.default_volatility
            ],
            buttons: [{
                text: _('Cancel'),
                handler: function() {
                    win.close();
                }
            }, {
                text: _('Confirm'),
                formBind: true,
                handler: function() {
                    if(form.isValid()) {
                        form.updateRecord(record);
                        win.close();
                    }
                }
            }]
        });

        win = desktop.createWindow({
            id: 'edit-rating-win',
            title: _('Edit rating'),
            iconCls: me.module.iconCls,
            width: size.width,
            height: size.height,
            modal: true,
            items: form,
            closable: false,
            minimizable: false,
            maximizable: false,
            resizable: false,
            tools: [{
                type: 'help',
                tooltip: _('Show help'),
                callback: function() {
                    var whsize = desktop.getReasonableWindowSize(800, 640);
                    var wh = Ext.create('SoL.window.Help', {
                        width: whsize.width,
                        height: whsize.height,
                        // TRANSLATORS: this is the URL of the manual
                        // page explaining championship insert/edit
                        help_url: _('/static/manual/en/ratings.html#insert-and-edit'),
                        title: _('Help on ratings insert/edit')
                    });
                    wh.show();
                }
            }]
        });

        form.loadRecord(record);

        win.show();
    }
});


Ext.define('SoL.module.Ratings', {
    extend: 'MP.desktop.Module',
    requires: [
        'MP.grid.Panel'
    ],
    uses: [
        'SoL.module.Ratings.Actions'
    ],

    id: 'ratings-win',
    iconCls: 'ratings-icon',
    launcherText: _('Ratings'),
    launcherTooltip: _('<b>Ratings</b><br />Basic ratings management'),

    config: {
        xtype: 'editable-grid',
        pageSize: 14,
        autoShowAllEditors: false,
        clicksToEdit: 0,
        dataURL: '/data/ratings',
        saveChangesURL: '/bio/saveChanges',
        sorters: ['description']
    },

    getConfig: function(callback) {
        var me = this;
        var cfg = me.config;

        if(!cfg.metadata) {
            MP.data.MetaData.fetch(cfg.dataURL, me, function(metadata) {
                var overrides = {};

                Ext.apply(cfg, {
                    metadata: metadata,
                    fields: metadata.fields(overrides),
                    columns: metadata.columns(overrides, false),
                    idProperty: metadata.primary_key,
                    totalProperty: metadata.count_slot,
                    successProperty: metadata.success_slot,
                    rootProperty: metadata.root_slot,
                    plugins: [
                        Ext.create('SoL.module.Ratings.Actions', {
                            module: me
                        })
                    ]
                });
                callback(cfg);
            });
        } else {
            callback(cfg);
        }
    },

    createOrShowWindow: function() {
        var me = this;
        var desktop = me.app.getDesktop();
        var win = desktop.getWindow(me.id);

        // If the window is already present, destroy and recreate it,
        // to reapply configuration and filters
        if(win) {
            win.destroy();
        }

        me.configure(
            [me.getConfig],
            function(done) {
                var size = desktop.getReasonableWindowSize(690, 421, "S");

                me.config.newRecordData = {
                    tau: 0.5,
                    default_rate: 1500,
                    default_deviation: 350,
                    default_volatility: 0.06
                };

                win = desktop.createWindow({
                    id: me.id,
                    title: me.launcherText,
                    taskbuttonTooltip: me.launcherTooltip,
                    iconCls: me.iconCls,
                    items: [me.config],
                    x: size.x,
                    y: size.y,
                    width: size.width,
                    height: size.height,
                    tools: [{
                        type: 'help',
                        tooltip: _('Show help'),
                        callback: function() {
                            var whsize = desktop.getReasonableWindowSize(800, 640);
                            var wh = Ext.create('SoL.window.Help', {
                                width: whsize.width,
                                height: whsize.height,
                                // TRANSLATORS: this is the URL of the manual
                                // page explaining ratings management
                                help_url: _('/static/manual/en/ratings.html'),
                                title: _('Help on ratings management')
                            });
                            wh.show();
                        }
                    }]
                });

                // Fetch the first page of records, and when done show
                // the window
                win.child('editable-grid').store.load({
                    params: {start: 0, limit: me.pageSize},
                    callback: function() {
                        win.on({show: done, single: true});
                        win.show();
                    }
                });
            }
        );
    }
});
