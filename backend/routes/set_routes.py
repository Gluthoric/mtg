from flask import Blueprint, jsonify, request
from models.set import Set
from database import db
from sqlalchemy import asc, desc

set_routes = Blueprint('set_routes', __name__)

@set_routes.route('/all-sets', methods=['GET'])
def get_all_sets():
    try:
        # Extract query parameters
        name = request.args.get('name', type=str, default='')
        set_type = request.args.get('set_type', type=str, default='')
        sort_by = request.args.get('sort_by', type=str, default='released_at')
        sort_order = request.args.get('sort_order', type=str, default='desc')
        page = request.args.get('page', type=int, default=1)
        per_page = request.args.get('per_page', type=int, default=20)

        query = Set.query

        # Apply filters
        if name:
            query = query.filter(Set.name.ilike(f'%{name}%'))
        if set_type:
            query = query.filter(Set.set_type == set_type)

        # Apply sorting
        if sort_order.lower() == 'asc':
            query = query.order_by(asc(getattr(Set, sort_by)))
        else:
            query = query.order_by(desc(getattr(Set, sort_by)))

        # Apply pagination
        paginated_sets = query.paginate(page=page, per_page=per_page, error_out=False)

        sets = [set.to_dict() for set in paginated_sets.items]

        return jsonify({
            'sets': sets,
            'total': paginated_sets.total,
            'pages': paginated_sets.pages,
            'current_page': paginated_sets.page
        }), 200
    except AttributeError:
        return jsonify({"error": f"Invalid sort_by field: {sort_by}"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Add more routes for sets if needed