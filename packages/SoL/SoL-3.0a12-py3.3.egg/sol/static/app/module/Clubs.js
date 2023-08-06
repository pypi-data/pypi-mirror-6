// -*- coding: utf-8 -*-
// :Progetto:  SoL -- Clubs window
// :Creato:    mer 15 ott 2008 09:09:47 CEST
// :Autore:    Lele Gaifax <lele@metapensiero.it>
// :Licenza:   GNU General Public License version 3 or later
//

/*jsl:declare Ext*/
/*jsl:declare _*/
/*jsl:declare MP*/
/*jsl:declare window*/
/*jsl:declare SoL*/
/*jsl:declare FileReader*/

Ext.define('SoL.module.Clubs.Actions', {
    extend: 'MP.action.StoreAware',

    uses: [
        'Ext.Action',
        'Ext.form.field.File',
        'MP.form.Panel'
    ],

    statics: {
        EDIT_CLUB_ACTION: 'edit_club',
        DOWNLOAD_TOURNEYS_ACTION: 'download_tourneys',
        SHOW_CHAMPIONSHIPS_ACTION: 'show_championships',
        SHOW_MEMBERS_ACTION: 'show_members',
        SHOW_ASSOCIATES_ACTION: 'show_associates'
    },

    initActions: function() {
        var me = this;
        var ids = me.statics();

        me.callParent();

        me.editClubAction = me.addAction(new Ext.Action({
            itemId: ids.EDIT_CLUB_ACTION,
            text: _('Modify'),
            tooltip: _('Edit selected club.'),
            iconCls: 'edit-record-icon',
            disabled: true,
            needsOneSelectedRow: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0];
                me.showEditClubWindow(record);
            }
        }));

        me.showChampionshipsAction = me.addAction(new Ext.Action({
            itemId: ids.SHOW_CHAMPIONSHIPS_ACTION,
            text: _('Championships'),
            tooltip: _('Show championships organized by this club.'),
            iconCls: 'championships-icon',
            disabled: true,
            needsOneSelectedRow: true,
            needsCleanStore: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0];
                var idclub = record.get('idclub');
                var club = record.get('description');
                var prizes = record.get('prizes');
                var couplings = record.get('couplings');
                var module = me.module.app.getModule('championships-win');
                module.createOrShowWindow(idclub, club, prizes, couplings);
            }
        }));

        me.showMembersAction = me.addAction(new Ext.Action({
            itemId: ids.SHOW_MEMBERS_ACTION,
            text: _('Members'),
            tooltip: _('Show players members of this club.'),
            iconCls: 'players-icon',
            disabled: true,
            needsOneSelectedRow: true,
            needsCleanStore: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0];
                var idclub = record.get('idclub');
                var club = record.get('description');
                var module = me.module.app.getModule('players-win');
                module.createOrShowWindow(null, null, idclub, club);
            }
        }));

        me.showAssociatesAction = me.addAction(new Ext.Action({
            itemId: ids.SHOW_ASSOCIATES_ACTION,
            text: _('Associates'),
            tooltip: _('Show players associated with this federation.'),
            iconCls: 'players-icon',
            disabled: true,
            needsOneSelectedRow: true,
            needsCleanStore: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0];
                var idclub = record.get('idclub');
                var club = record.get('description');
                var module = me.module.app.getModule('players-win');
                module.createOrShowWindow(null, null, idclub, club, true);
            }
        }));

        me.downloadTourneysAction = me.addAction(new Ext.Action({
            itemId: ids.DOWNLOAD_TOURNEYS_ACTION,
            text: _('Download'),
            tooltip: _('Download data of all the tourneys in every championship organized by this club.'),
            iconCls: 'download-icon',
            disabled: true,
            needsOneSelectedRow: true,
            needsCleanStore: true,
            handler: function() {
                var record = me.component.getSelectionModel().getSelection()[0];
                var idclub = record.get('idclub');
                var url = '/bio/dump?idclub=' + idclub;
                window.open(url, "_blank");
            }
        }));
    },

    attachActions: function() {
        var me = this;

        me.callParent();

        var tbar = me.component.child('#ttoolbar');

        tbar.add(2, ' ',
                 me.editClubAction,
                 me.showChampionshipsAction, {
                     text: _('Players'),
                     iconCls: 'players-icon',
                     menu: { items: [me.showMembersAction,
                                     me.showAssociatesAction] }
                 },
                 me.downloadTourneysAction);

        me.component.on({
            itemdblclick: function() {
                me.editClubAction.execute();
            }
        });
        me.component.store.on({
            add: function(store, records) {
                //jsl:unused store
                var record = records[0];
                me.showEditClubWindow(record);
            }
        });
    },

    shouldDisableAction: function(act) {
        var me = this;
        var disable = me.component.shouldDisableAction(act);

        if(!disable && act.itemId == me.statics().SHOW_ASSOCIATES_ACTION) {
            var record = me.component.getSelectionModel().getSelection()[0];
            if(!record.get('isfederation')) {
                disable = true;
            }
        }
        return disable;
    },

    readImageAsDataURL: function(event, elt, form) {
        var file = elt.files[0];

        if(file.type.split('/')[0] == 'image') {
            var reader = new FileReader();

            form._emblem = file.name;

            reader.onload = function(e) {
                var img = e.target.result;
                if(img.length > 256000) {
                    Ext.MessageBox.alert(_('Error'),
                                         _('Image too big, max 256k allowed'));
                    form._emblem = null;
                } else {
                    form.down('image').setSrc(img);
                }
            };

            reader.onerror = function() {
                Ext.MessageBox.alert(_('Error'),
                                     _('Sorry, could not read image file')
                                     + ': ' + reader.error);
                form._emblem = null;
            };

            reader.readAsDataURL(file);
        } else {
            Ext.MessageBox.alert(_('Error'),
                                 _('Only image files allowed'));
        }
    },

    deleteImage: function(form) {
        form._emblem = '';
        form.down('image').setSrc('');
    },

    showEditClubWindow: function(record) {
        var me = this;
        var desktop = me.module.app.getDesktop();
        var win = desktop.getWindow('edit-club-win');

        // If the window is already present, destroy and recreate it,
        // to reapply configuration and filters
        if(win) {
            win.destroy();
        }

        var metadata = me.module.config.metadata;
        var size = desktop.getReasonableWindowSize(650, 420);
        var editors = metadata.editors({
            '*': {
                editor: MP.form.Panel.getDefaultEditorSettingsFunction('100%')
            },
            nationality: { editor: { xtype: 'flagscombo' } }
        });
        var form = Ext.create('MP.form.Panel', {
            autoScroll: true,
            fieldDefaults: {
                labelWidth: 150,
                margin: '15 10 0 10'
            },
            items: [{
                xtype: 'container',
                layout: 'hbox',
                items: [{
                    xtype: 'container',
                    layout: 'anchor',
                    flex: 1,
                    items: [
                        editors.description,
                        editors.siteurl,
                        editors.email,
                        editors.nationality,
                        editors.isfederation,
                        editors.couplings,
                        editors.prizes
                    ]
                }, {
                    xtype: 'container',
                    style: 'text-align: center;',
                    width: 170,
                    items: [{
                        xtype: 'image',
                        margin: '70 10 0 10',
                        border: 1,
                        style: {
                            maxWidth: '150px',
                            maxHeight: '150px',
                            borderColor: 'lightgray',
                            borderStyle: 'solid'
                        }
                    }, {
                        xtype: 'filefield',
                        name: 'emblem',
                        fieldLabel: '',
                        labelWidth: 0,
                        buttonOnly: true,
                        buttonText: _('Change emblem...'),
                        style: 'text-align: center;',
                        listeners: {
                            afterrender: function(fld) {
                                var el = fld.fileInputEl.dom;
                                el.setAttribute('accept', 'image/*');
                            },
                            el: {
                                change: {
                                    fn: function(event, elt) {
                                        if(elt.files.length)
                                            me.readImageAsDataURL(event, elt, form);
                                    }
                                }
                            }
                        }
                    }, {
                        xtype: 'button',
                        text: _('Delete emblem'),
                        handler: function() {
                            me.deleteImage(form);
                        }
                    }]
                }]
            }],
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
                        if(form._emblem !== undefined) {
                            record.set('emblem', form._emblem);
                            record.set('image', form.down('image').src);
                        }
                        win.close();
                    }
                }
            }]
        });

        win = desktop.createWindow({
            id: 'edit-club-win',
            title: _('Edit club'),
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
                        // page explaining club insert/edit
                        help_url: _('/static/manual/en/clubs.html#insert-and-edit'),
                        title: _('Help on club insert/edit')
                    });
                    wh.show();
                }
            }]
        });

        form.loadRecord(record);

        if(!Ext.isEmpty(record.get('emblem')) || !Ext.isEmpty(record.get('image'))) {
            var emblem = form.down('image');
            if(!Ext.isEmpty(record.get('image'))) {
                emblem.setSrc(record.get('image'));
            } else {
                emblem.setSrc('/lit/emblem/' + record.get('emblem'));
            }
        }

        win.show();
    }
});


Ext.define('SoL.module.Clubs', {
    extend: 'MP.desktop.Module',
    requires: [
        'MP.grid.Panel'
    ],
    uses: [
        'SoL.module.Clubs.Actions',
        'SoL.form.field.FlagsCombo'
    ],

    id: 'clubs-win',
    iconCls: 'clubs-icon',
    launcherText: _('Clubs'),
    launcherTooltip: _('<b>Clubs</b><br />Basic clubs management'),

    config: {
        xtype: 'editable-grid',
        pageSize: 14,
        autoShowAllEditors: false,
        clicksToEdit: 0,
        dataURL: '/data/clubs',
        saveChangesURL: '/bio/saveChanges',
        sorters: ['description']
    },

    getConfig: function(callback) {
        var me = this;
        var cfg = me.config;

        if(!cfg.metadata) {
            MP.data.MetaData.fetch(cfg.dataURL, me, function(metadata) {
                var overrides = {
                    nationality: {
                        renderer: SoL.form.field.FlagsCombo.renderer,
                        editor: { xtype: 'flagscombo' }
                    }
                };
                var fields = metadata.fields(overrides);

                fields.push({
                    name: 'image',
                    type: 'string',
                    sendBackToServer: true
                });

                Ext.apply(cfg, {
                    metadata: metadata,
                    fields: fields,
                    columns: metadata.columns(overrides, false),
                    idProperty: metadata.primary_key,
                    totalProperty: metadata.count_slot,
                    successProperty: metadata.success_slot,
                    rootProperty: metadata.root_slot,
                    plugins: [
                        Ext.create('SoL.module.Clubs.Actions', {
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
                var size = desktop.getReasonableWindowSize(650, 447, "NW");

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
                                // page explaining clubs management
                                help_url: _('/static/manual/en/clubs.html'),
                                title: _('Help on clubs management')
                            });
                            wh.show();
                        }
                    }]
                });

                var grid = win.child('editable-grid');

                // Fetch the first page of records, and when done show
                // the window
                grid.store.load({
                    params: {start: 0, limit: me.pageSize},
                    callback: function() {
                        win.on({show: done, single: true});
                        win.show();
                    }
                });

                var da = grid.findActionById('delete');
                da.shouldBeDisabled = me.shouldDisableDeleteAction.bind(grid);
            }
        );
    },

    shouldDisableDeleteAction: function() {
        var grid = this;
        var sm = grid.getSelectionModel();

        if(sm.getCount() > 0) {
            var selrecs = sm.getSelection();
            var disable = false;

            for(var i=selrecs.length-1; i>=0; i--) {
                if(selrecs[i].get('Championships') > 0) {
                    disable = true;
                    break;
                }
            }
            return disable;
        } else {
            return true;
        }
    }
});
