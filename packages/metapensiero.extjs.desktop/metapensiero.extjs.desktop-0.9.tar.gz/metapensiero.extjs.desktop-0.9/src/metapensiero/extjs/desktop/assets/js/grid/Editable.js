//  -*- coding: utf-8 -*-
// :Progetto:  metapensiero.extjs.desktop -- Editable grid
// :Creato:    mer 05 dic 2012 15:35:03 CET
// :Autore:    Lele Gaifax <lele@metapensiero.it>
// :Licenza:   GNU General Public License version 3 or later
//

/*jsl:declare Ext*/
/*jsl:declare MP*/


Ext.define('MP.grid.Editable', {
    extend: 'MP.grid.Basic',

    requires: [
        'Ext.grid.plugin.CellEditing',
        'MP.action.AddAndDelete'
    ],

    /**
     * @cfg {Bool} noAddAndDelete
     * Set it to true to disable the automatic creation of the “add”
     * and “delete” actions
     */
    noAddAndDelete: false,

    initComponent: function() {
        var me = this;

        if(!me.readOnly) {
            Ext.each(me.columns, function(c) {
                if(c.editor && c.editor.lookupFor) {
                    var fname = c.editor.lookupFor;
                    var iname = c.editor.store.proxy.reader.idProperty;
                    var listeners = {
                        change: function(combo) {
                            if(combo.getRawValue()==='') {
                                var record = me.getSelectionModel().getSelection()[0];
                                record.set(fname, null);
                            }
                        },
                        select: function(combo, selected) {
                            //jsl:unused combo
                            var record = me.getSelectionModel().getSelection()[0];
                            record.set(fname, selected[0].get(iname));
                        }
                    };
                    if(c.editor.isComponent) {
                        c.editor.on(listeners);
                    } else {
                        if(c.editor.listeners) {
                            Ext.apply(c.editor.listeners, listeners);
                        } else {
                            c.editor.listeners = listeners;
                        }
                    }
                }
            });

            var cellEditing = null;

            if(me.clicksToEdit) {
                cellEditing = Ext.create('Ext.grid.plugin.CellEditing', {
                    clicksToEdit: me.clicksToEdit
                });
            }

            if(!me.plugins) {
                me.plugins = [];
            }

            if(cellEditing) {
                me.plugins.push(cellEditing);

                // End cell editing when switching to another tab
                // panel
                me.on('hide', function() {
                    me.editingPlugin.completeEdit();
                });
            }

            if(!me.noAddAndDelete) {
                me.plugins.push(Ext.create('MP.action.AddAndDelete'));
            }
        }

        me.callParent();
    },

    initEvents: function() {
        var me = this;

        me.callParent();

        if(!me.readOnly) {
            me.on("rowcontextmenu", function(egrid, index, e) {
                var items = [];
                var sm = egrid.getSelectionModel();
                var addndel = MP.action.AddAndDelete;

                sm.selectRow(index, false);
                Ext.each(me.getAllActions(), function(act) {
                    if(act.itemId != addndel.ADD_ACTION && act.itemId != addndel.DELETE_ACTION
                       && act.initialConfig && act.initialConfig.listeners
                       && !act.disabled) {
                        items.push({
                            text: act.text,
                            tooltip: act.initialConfig.tooltip,
                            iconCls: act.initialConfig.iconCls,
                            handler: act.execute
                        });
                    }
                });
                e.stopEvent();
                if(items.length>0) {
                    var pm = new Ext.menu.Menu(items);
                    var coords = e.getXY();
                    pm.showAt([coords[0], coords[1]]);
                }
            });
        }
    }
});
