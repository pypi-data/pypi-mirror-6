// -*- coding: utf-8 -*-
// :Progetto:  SoL -- Matches panel of the tourney management
// :Creato:    gio 20 nov 2008 18:23:54 CET
// :Autore:    Lele Gaifax <lele@metapensiero.it>
// :Licenza:   GNU General Public License version 3 or later
//

/*jsl:declare Ext*/
/*jsl:declare _*/
/*jsl:declare MP*/
/*jsl:declare window*/
/*jsl:declare SoL*/


Ext.define('SoL.view.Matches.Actions', {
    extend: 'MP.action.Plugin',
    uses: ['Ext.Action'],

    statics: {
        NEW_TURN_ACTION: 'new_turn',
        SHOW_CLOCK_ACTION: 'show_clock',
        PRINT_CARDS_ACTION: 'print_cards',
        PRINT_RESULTS_ACTION: 'print_results',
        PRINT_MATCHES_ACTION: 'print_matches'
    },

    initActions: function() {
        var me = this;
        var ids = me.statics();
        var tourney = me.module.tourney;

        me.callParent();

        me.newTurnAction = me.addAction(new Ext.Action({
            itemId: ids.NEW_TURN_ACTION,
            text: _('New turn'),
            tooltip: _('Create next turn.'),
            iconCls: 'new-turn-icon',
            disabled: tourney.currentturn != tourney.rankedturn,
            hidden: me.component.readOnly,
            scope: me.component,
            handler: me.component.newTurn
        }));

        me.showClockAction = me.addAction(new Ext.Action({
            itemId: ids.SHOW_CLOCK_ACTION,
            text: _('Show clock'),
            tooltip: _('Show an alarm clock for the current turn.'),
            iconCls: 'alarm-clock-icon',
            disabled: me.component.readOnly,
            hidden: me.component.readOnly,
            handler: function() {
                var url = '/tourney/clock?idtourney=' +
                    tourney.idtourney;
                window.open(url, "_blank");
            }
        }));

        me.printCardsAction = me.addAction(new Ext.Action({
            itemId: ids.PRINT_CARDS_ACTION,
            text: _('Scorecards'),
            tooltip: _('Print current turn scorecards.'),
            iconCls: 'print-icon',
            disabled: me.component.readOnly,
            hidden: me.component.readOnly,
            handler: function() {
                var url = '/pdf/scorecards?idtourney=' +
                    tourney.idtourney;
                window.location.assign(url);
            }
        }));

        me.printResultsAction = me.addAction(new Ext.Action({
            itemId: ids.PRINT_RESULTS_ACTION,
            text: _('Results'),
            tooltip: _('Print current turn results.'),
            iconCls: 'print-icon',
            disabled: me.component.readOnly,
            hidden: me.component.readOnly,
            handler: function() {
                var url = '/pdf/results?idtourney=' +
                    tourney.idtourney;
                window.location.assign(url);
            }
        }));

        me.printMatchesAction = me.addAction(new Ext.Action({
            text: _('Matches'),
            tooltip: _('Print next turn matches.'),
            iconCls: 'print-icon',
            disabled: me.component.readOnly,
            hidden: me.component.readOnly,
            handler: function() {
                var url = '/pdf/matches?idtourney=' +
                    tourney.idtourney;
                window.location.assign(url);
            }
        }));
    },

    attachActions: function() {
        var me = this;

        me.callParent();

        var tbar = me.component.child('#ttoolbar');

        tbar.add(0, me.newTurnAction, me.showClockAction, ' ',
                 me.printMatchesAction,
                 me.printCardsAction,
                 me.printResultsAction);
    }
});

Ext.define('SoL.view.Matches', {
    extend: 'MP.grid.Panel',

    alias: 'widget.matches-grid',

    requires: [
        'SoL.view.Matches.Actions'
    ],

    statics: {
        ordinals: [
            '',
            _('first'),
            _('second'),
            _('third'),
            _('fourth'),
            _('fifth'),
            _('sixth'),
            _('seventh'),
            _('eighth'),
            _('nineth'),
            _('tenth'),
            _('eleventh'),
            _('twelfth'),
            _('thirdteenth'),
            _('fourteenth'),
            _('fifteenth')
        ],

        getConfig: function(callback, errorcb, config) {
            //jsl:unused errorcb
            var me = this; /* NB: this is the Tourney module */
            var ordinals = SoL.view.Matches.ordinals;
            var cfg = config.Matches = {
                dataURL: '/tourney/matches',
                filters: [{id: 'turn',
                           property: 'turn',
                           value: config.tourney.currentturn}],
                header: true,
                layout: 'fit',
                lbar: [],
                noAddAndDelete: true,
                noBottomToolbar: true,
                noSaveAndResetActions: config.tourney.prized,
                noFilterbar: true,
                pageSize: 999,
                plugins: [
                    Ext.create('SoL.view.Matches.Actions', {
                        module: me
                    })
                ],
                readOnly: config.tourney.prized,
                saveChangesURL: '/bio/saveChanges',
                sorters: ['turn', 'board'],
                title: (config.tourney.currentturn === 0
                        ? _('Matches')
                        : Ext.String.format(
                            _('Matches of the {0} turn'),
                            ordinals[config.tourney.currentturn])),
                xtype: 'matches-grid'
            };

            for(var i=1; i <= config.tourney.currentturn; i++) {
                cfg.lbar.push({
                    itemId: 'turn-' + i,
                    text: i,
                    cls: i==config.tourney.currentturn ? 'active-turn' : '',
                    tooltip: Ext.String.format(
                        _('Show {0} turn matches.'), ordinals[i]),
                    turn: i,
                    handler: function(btn) {
                        me.matches_grid.filterOnTurn(btn.turn);
                    }
                });
            }

            cfg.lbar.push('-', {
                iconCls: 'icon-cross',
                tooltip: _('Remove last turn.'),
                handler: function(btn) {
                    var grid = btn.up().up();
                    var turn = config.tourney.currentturn;

                    if(turn) {
                        var title = _('Delete last turn?');
                        var msg = Ext.String.format(
                            _('Do you really want to delete the {0} turn?<br/>This is <b>NOT</b> revertable!'),
                            ordinals[turn]);
                        Ext.Msg.confirm(title, msg, function(response) {
                            if('yes' == response) {
                                grid.deleteTurn(turn);
                            }
                        });
                    }
                }
            });

            MP.data.MetaData.fetch(cfg.dataURL, me, function(metadata) {
                var overrides = {
                    score1: { editor: { hideTrigger: true } },
                    score2: { editor: { hideTrigger: true } }
                };

                Ext.apply(cfg, {
                    metadata: metadata,
                    fields: metadata.fields(overrides),
                    columns: metadata.columns(overrides),
                    idProperty: metadata.primary_key,
                    totalProperty: metadata.count_slot,
                    successProperty: metadata.success_slot,
                    rootProperty: metadata.root_slot
                });
                callback(cfg);
            });
        }
    },

    initComponent: function() {
        var me = this;

        me.callParent(arguments);

        if(!me.readOnly) {
            me.on("beforeedit", function(editor, event) {
                //jsl:unused editor
                var rec = event.record;
                var cturn = me.module.tourney.currentturn;
                var phantom = rec.get("idcompetitor2") === '';
                return (!phantom && rec.get("turn") == cturn);
            });
        } else {
            this.on("beforeedit", function() {
                return false;
            });
        }

        // Install a KeyMap on the grid that allows jumping to a given record
        // (and eventually start editing its score1 column) simply by digiting
        // its position

        var rownum = '';
        var gotoRowNum = Ext.Function.createBuffered(function() {
            var sm = me.getSelectionModel();
            var row = parseInt(rownum, 10) - 1;
            var ep = me.editingPlugin;

            sm.select(row);
            if(ep) {
                ep.startEdit(row, me.getColumnByName('score1'));
            }

            rownum = '';
        }, 400);

        me.jumpToRecordKeyMap = new Ext.util.KeyMap({
            target: me.getView(),
            eventName: 'itemkeydown',
            processEvent: function(view, record, node, index, event) {
                return event;
            },
            binding: {
                key: "1234567890",
                fn: function(keyCode, e) {
                    rownum = rownum + (e.getKey() - 48);
                    gotoRowNum();
                }
            }
        });
    },

    onDestroy: function() {
        if(this.jumpToRecordKeyMap) {
            Ext.destroy(this.jumpToRecordKeyMap);
            delete this.jumpToRecordKeyMap;
        }
        this.callParent();
    },

    newTurn: function() {
        var me = this;
        var ordinals = me.statics().ordinals;
        var tourney = me.module.tourney;
        var lbar = me.child('toolbar[dock="left"]');

        if(me.focusedCompetitor) {
            lbar.show();
            me.getColumnByName('turn').hide();
            me.getColumnByName('board').show();
            me.filterOnTurn(tourney.currentturn);
            me.focusedCompetitor = null;
        }

        Ext.Ajax.request({
            url: '/tourney/newTurn',
            params: { idtourney: tourney.idtourney },
            success: function (r) {
                var res = Ext.decode(r.responseText);
                if(!res) {
                    Ext.MessageBox.alert(
                        _("Comunication error"),
                        _('Cannot decode JSON object'));
                } else {
                    if(res.success) {
                        var cturn = res.currentturn;

                        tourney.currentturn = cturn;
                        tourney.rankedturn = res.rankedturn;
                        tourney.prized = res.prized;

                        lbar.insert(cturn-1, Ext.create('Ext.button.Button', {
                            itemId: 'turn-' + cturn,
                            text: cturn,
                            tooltip: Ext.String.format(
                                _('Show {0} turn matches.'),
                                ordinals[cturn]),
                            turn: cturn,
                            handler: function(btn) {
                                me.filterOnTurn(btn.turn);
                            }
                        }));
                        me.filterOnTurn(cturn);
                        me.updateActions();
                    } else {
                        Ext.MessageBox.alert(_('Error'), res.message);
                    }
                }
            }
        });
    },

    deleteTurn: function(turn) {
        var me = this;
        var tourney = me.module.tourney;

        Ext.Ajax.request({
            url: '/tourney/deleteFromTurn',
            params: { idtourney: tourney.idtourney, fromturn: turn },
            success: function (r) {
                var res = Ext.decode(r.responseText);
                if(!res) {
                    Ext.MessageBox.alert(
                        _("Comunication error"),
                        _('Cannot decode JSON object'));
                } else {
                    if(res.success) {
                        var lbar = me.child('toolbar[dock="left"]');

                        tourney.currentturn = res.currentturn;
                        tourney.rankedturn = res.rankedturn;
                        tourney.prized = res.prized;

                        if(turn > 1) {
                            me.filterOnTurn(turn - 1);
                        } else {
                            me.setTitle(_('Matches'));
                            me.store.removeAll();
                        }
                        me.module.reloadRanking();
                        lbar.remove('turn-' + turn, true);

                        me.updateActions();
                    } else {
                        Ext.MessageBox.alert(_('Error'), res.message);
                    }
                }
            }
        });
    },

    filterOnTurn: function(turn) {
        var me = this;
        var ordinals = me.statics().ordinals;
        var store = me.store;

        if(store.isModified()) {
            Ext.MessageBox.alert(
                _('Uncommitted changes'),
                _('There are uncommitted changes, cannot switch to a different turn!'));
            return;
        }

        store.filter({
            id: 'turn',
            property: 'turn',
            value: turn
        });

        me.setTitle(Ext.String.format(_('Matches of the {0} turn'),
                                      ordinals[turn]));
        me.child('toolbar[dock="left"]').cascade(function(btn) {
            if(btn.turn == turn) {
                btn.addCls('active-turn');
            } else {
                btn.removeCls('active-turn');
            }
        });
    },

    commitChanges: function() {
        var me = this;
        var ok = true;

        me.store.each(function(rec) {
            if(rec.get("score1") === 0 && rec.get("score2") === 0) {
                ok = false;
                me.getSelectionModel().select([rec]);
                Ext.MessageBox.alert(
                    _('Invalid scores'),
                    _('There is at least one match without result!'));
                return false;
            } else
                return true;
        });

        if(ok) {
            me.store.commitChanges(me.saveChangesURL, 'idmatch', function() {
                var tourney = me.module.tourney;

                Ext.Ajax.request({
                    url: '/tourney/updateRanking',
                    params: { idtourney: tourney.idtourney },
                    success: function (r) {
                        var res = Ext.decode(r.responseText);
                        if(!res) {
                            Ext.MessageBox.alert(
                                _("Comunication error"),
                                _('Cannot decode JSON object'));
                        } else {
                            if(res.success) {
                                me.module.reloadRanking();
                                tourney.currentturn = res.currentturn;
                                tourney.rankedturn = res.rankedturn;
                                tourney.prized = res.prized;
                                me.updateActions();
                            } else {
                                Ext.MessageBox.alert(_('Error'), res.message);
                            }
                        }
                    }
                });
            });
        }
    },

    updateActions: function() {
        var me = this;
        var tourney = me.module.tourney;
        var nta = me.findActionById('new_turn');
        var lbar = me.child('toolbar[dock="left"]');

        nta.setDisabled(!tourney.partecipants ||
                        (tourney.currentturn > 0
                         && tourney.currentturn != tourney.rankedturn));
        nta.setHidden(tourney.prized);
        lbar.cascade(function(btn) {
            if(btn.xtype == 'tbseparator' || btn.iconCls == 'icon-cross') {
                btn.setVisible(!tourney.prized && tourney.currentturn > 0);
            }
        });
    }
});
