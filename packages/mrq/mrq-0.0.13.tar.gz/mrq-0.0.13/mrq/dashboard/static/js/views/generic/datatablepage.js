define(["views/generic/page", "underscore", "jquery"],function(Page, _, $) {

  var noop = function() {};

 /**
   * A page with a main DataTable instance bound to this.col
   *
   */
  return Page.extend({

    init: function() {

      this.filters = {};

      this.delegateEvents(_.extend({
        "click .js-datatable-filters-submit": "filterschanged"
      }, this.events));

      this.on("show", function() {
        this.listenTo(this.app.rootView, "visibilitychange", this.refreshDataTable);
      }, this);

      this.on("hide", function() {
        this.stopListening();
      }, this);

      this.initFilters();

      this.refreshDataTable(true);

    },

    initFilters: function() {
      // Overload me!
    },

    getCommonDatatableConfig:function(unit_name) {

      var self = this;

      return {
        "sPaginationType": "full_numbers",
        "iDisplayLength":20,
        "fnDrawCallback":function() {
          //self.$('.js-datatable .tooltip-top').tooltip();
          //self.$(".dataTables_filter input").prop("type","search").attr("results","10").attr("placeholder","Search products...");
        },
        //"bLengthChange":false,
        //"aLengthMenu": [[25, 50, 100], [25, 50, 100]],
        "sDom":"rtipl",
        "oLanguage":{
          "sSearch":"",
          "sInfo": "Showing _START_ to _END_ of _TOTAL_ "+unit_name,
          "sEmptyTable":"No "+unit_name,
          "sInfoEmpty":"Showing 0 "+unit_name,
          "sInfoFiltered": "",
          "sLengthMenu": '<select style="width:60px;font-size:13px;height:26px;">'+
            '<option value="20">20</option>'+
            '<option value="50">50</option>'+
            '<option value="100">100</option>'+
            '</select>'
        },
        "sPaginationType": "bs_full",
        "bProcessing": true,
        "bServerSide": true,
        "bDeferRender": true,
        "bDestroy": true,
        "sAjaxSource": "/api/datatables/"+unit_name,
        "fnServerData": function (sSource, aoData, fnCallback) {

          _.each(self.filters, function(v, k) {
            aoData.push({"name": k, "value": v});
          });

          $.getJSON( sSource, aoData, function (json) {
            fnCallback(json);
            self.trigger("loaded");
          });
        }
      };
    },



    initDataTable:function(config) {

      this.dataTable = this.$(".js-datatable").dataTable(config);

      // SEARCH - Add the placeholder for Search and Turn this into in-line form control
      var search_input = this.dataTable.closest('.dataTables_wrapper').find('div[id$=_filter] input');
      search_input.attr('placeholder', 'Search');
      search_input.addClass('form-control input-sm');
      // LENGTH - Inline-Form control
      var length_sel = this.dataTable.closest('.dataTables_wrapper').find('div[id$=_length] select');
      length_sel.addClass('form-control input-sm');

      if (this.col) {
        this.col.on("remove",function(m,c,options) {
          noop(m,c); //required for jshint :/
          if (this.dataTable) {
            this.dataTable.fnDeleteRow(options.index);
          }
        },this);
        this.col.on("add",function(m,c/*,options*/) {
          noop(c); //required for jshint :/
          if (this.dataTable) {
            this.dataTable.fnAddData([m.toJSON()]);
          }
        },this);
      }

      this.dataTable.fnSetFilteringDelay();

    },

    refreshDataTable:function(justQueue) {

      if (!this.dataTable) return this.flush();

      var self = this;

      var REFRESH_INTERVAL = parseInt($(".js-autorefresh").val(), 10) * 1000;

      if (!this.app.rootView.isTabVisible) {
        REFRESH_INTERVAL = 0;
      }

      clearTimeout(self.refreshDataTableTimeout);

      if (!REFRESH_INTERVAL) return;

      var queue = function() {
        self.refreshDataTableTimeout = setTimeout(function() {
          self.refreshDataTable();
        }, REFRESH_INTERVAL);
      };

      var el = self.$(".js-datatable");

      // We may have navigated away in the meantime
      if (!el.is(":visible")) return;

      // Don't reload when a modal is shown
      if ($(".modal:visible").length) {
        $(".modal:visible").trigger("poll");
        justQueue = true;
      }

      if (justQueue) {
        queue();
      } else {
        this.once("loaded", queue);
        this.dataTable.fnReloadAjax();
      }

    },

    renderFilters: function() {
      var self = this;

      if (!this._rendered) return;

      // if (this.filters["manufacturer"]) {
      //   this.$('.js-filter-manufacturer .js-filter-txt').html("Manufacturer: "+this.filters["manufacturer"]["name"]);
      // }

    },


    filterschanged:function(evt) {

      var self = this;

      if (evt) {
        evt.preventDefault();
        evt.stopPropagation();
      }

      _.each(self.filters, function(v, k) {
        self.filters[k] = self.$(".js-datatable-filters-"+k).val();
      });

      this.refreshDataTable();
    },

    render: function() {

      this.renderTemplate({"filters": this.filters||{}});

      this.renderFilters();

      this.renderDatatable();

      return this;
    }

      /*

      TODO

      this.col.on("change",function() {
        if (this.dataTable) this.dataTable.fnReloadAjax();
      },this);
      */

  });

});
