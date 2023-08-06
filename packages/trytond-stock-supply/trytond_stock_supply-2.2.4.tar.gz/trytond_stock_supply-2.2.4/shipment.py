#This file is part of Tryton.  The COPYRIGHT file at the top level of
#this repository contains the full copyright notices and license terms.
from trytond.model import ModelView, ModelSQL
from trytond.transaction import Transaction
from trytond.pool import Pool


class ShipmentInternal(ModelSQL, ModelView):
    _name = 'stock.shipment.internal'

    def init(self, module_name):
        cursor = Transaction().cursor
        # Migration from 1.2: packing renamed into shipment
        cursor.execute("UPDATE ir_model_data "\
                "SET fs_id = REPLACE(fs_id, 'packing', 'shipment') "\
                "WHERE fs_id like '%%packing%%' AND module = %s",
                (module_name,))
        cursor.execute("UPDATE ir_model "\
                "SET model = REPLACE(model, 'packing', 'shipment') "\
                "WHERE model like '%%packing%%' AND module = %s",
                (module_name,))
        super(ShipmentInternal, self).init(module_name)

    def generate_internal_shipment(self):
        """
        Generate internal shipments to meet order points defined on
        non-warehouse location.
        """
        pool = Pool()
        order_point_obj = pool.get('stock.order_point')
        uom_obj = pool.get('product.uom')
        product_obj = pool.get('product.product')
        date_obj = pool.get('ir.date')
        user_obj = pool.get('res.user')
        user_record = user_obj.browse(Transaction().user)
        today = date_obj.today()
        # fetch quantities on order points
        op_ids = order_point_obj.search([
            ('type', '=', 'internal'),
            ])
        order_points = order_point_obj.browse(op_ids)
        id2product = {}
        location_ids = []
        for op in order_points:
            id2product[op.product.id] = op.product
            location_ids.append(op.storage_location.id)

        with Transaction().set_context(stock_date_end=today):
            pbl = product_obj.products_by_location(location_ids, 
                    list(id2product.iterkeys()), with_childs=True)

        # Create a list of move to create
        moves = {}
        for op in order_points:
            qty = pbl.get((op.storage_location.id, op.product.id), 0)
            if qty < op.min_quantity:
                key = (op.provisioning_location.id,
                       op.storage_location.id,
                       op.product.id)
                moves[key] = op.max_quantity - qty

        # Compare with existing draft shipments
        shipment_ids = self.search([
            ('state', '=', 'draft'), ['OR', 
                ('planned_date', '<=', today),
                ('planned_date', '=', False),
                ],
            ])
        for shipment in self.browse(shipment_ids):
            for move in shipment.moves:
                key = (shipment.from_location.id,
                       shipment.to_location.id,
                       move.product.id)
                if key not in moves:
                    continue
                quantity = uom_obj.compute_qty( move.uom, move.quantity,
                    id2product[move.product.id].default_uom)
                moves[key] = max(0, moves[key] - quantity)

        # Group moves by {from,to}_location
        shipments = {}
        for key,qty in moves.iteritems():
            from_location, to_location, product = key
            shipments.setdefault(
                (from_location, to_location),[]).append((product, qty))
        # Create shipments and moves
        for shipment, moves in shipments.iteritems():
            from_location, to_location = shipment
            values = {
                'from_location': from_location,
                'to_location': to_location,
                'planned_date': today,
                'moves': [],
                }
            for move in moves:
                product, qty = move
                values['moves'].append(
                    ('create',
                     {'from_location': from_location,
                      'to_location': to_location,
                      'product': product,
                      'quantity': qty,
                      'uom': id2product[product].default_uom.id,
                      'company': user_record.company.id,}
                     ))
            self.create(values)

ShipmentInternal()
