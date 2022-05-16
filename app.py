import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy 
from time import time

# Init app
app = Flask(__name__)

basedir = os.path.abspath(os.path.dirname(__file__))

# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Init db
db = SQLAlchemy(app)

"""       Table Models        """

class Instance(db.Model):
    instance_name = db.Column(db.String(250))
    instance_id = db.Column(db.Integer, primary_key=True)
    usage_type = db.Column(db.String(250))
    team_id = db.Column(db.Integer)
    status = db.Column(db.String(250))
    member_id = db.Column(db.Integer)
    permission_level = db.Column(db.String(250))

class Teams(db.Model):
    team_id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(250))
    owner = db.Column(db.String(250))
    instance_id = db.Column(db.Integer)
    modules_owned = db.Column(db.String(250))

class Members(db.Model):
    member_id = db.Column(db.Integer, primary_key=True)
    member_name = db.Column(db.String(250))
    email = db.Column(db.String(250))
    team_id = db.Column(db.Integer,db.ForeignKey(Teams.team_id))
    role = db.Column(db.String(250))
    permission_level = db.Column(db.String(250))

class Deploy(db.Model):
    deploy_id = db.Column(db.Integer, primary_key=True)
    member_id = db.Column(db.Integer)
    instance_id = db.Column(db.Integer)
    branch = db.Column(db.String(250))
    reason = db.Column(db.String(250))
    start_time = time
    end_time = time


# db.create_all()

"""    Instance Api Methods   """

# List All Teams
@app.route('/api/v1/teams', methods=['GET'])
def get_all_teams():
    teams = Teams.query.all()
    output = []
    for team in teams:
        team_data = {}
        team_data['team_id'] = team.team_id
        team_data['team_name'] = team.team_name
        team_data['owner'] = team.owner
        team_data['instance_id'] = team.instance_id
        team_data['modules_owned'] = team.modules_owned
        output.append(team_data)

    return jsonify ({'teams':output})


# List Instances By Team
@app.route('/api/v1/instances/team/<team_id>', methods=['GET'])
def get_all_instances(team_id):
    instances = Instance.query.filter_by(team_id=team_id).all()
    output = []
    for instance in instances:
        instance_data = {}
        instance_data['instance_id'] = instance.instance_id
        instance_data['instance_name'] = instance.instance_name
        instance_data['usage_type'] = instance.usage_type
        instance_data['team_id'] = instance.team_id
        instance_data['status'] = instance.status
        instance_data['member_id']= instance.member_id
        instance_data['permission_level'] = instance.permission_level
        output.append(instance_data)

    return jsonify ({'instances':output})

#Create Instance For Team
@app.route('/api/v1/instance/team/<team_id>', methods=['POST'])
def create_instance_for_team():

    data = request.get_json()
    new_instance = Instance(instance_name = data['instance_name'],instance_id = data['instance_id'], usage_type = data['usage_type'], team_id = data['team_id'], status = data['status'], member_id = data['member_id'], permission_level = data['permission_level'])
    db.session.add(new_instance)
    db.session.commit()

    return jsonify({'message':'New Instance Created'})

# View Instance By Instance ID
@app.route('/api/v1/instance/<instance_id>', methods=['GET'])
def get_one_instance(instance_id):

    instance = Instance.query.filter_by(instance_id=instance_id).first()

    if not instance:
        return jsonify ({'message':'No Instance Found!'})
    instance_data = {}
    instance_data['instance_id'] = instance.instance_id
    instance_data['instance_name'] = instance.instance_name
    instance_data['usage_type'] = instance.usage_type
    instance_data['team_id'] = instance.team_id
    instance_data['status'] = instance.status
    instance_data['member_id']= instance.member_id
    instance_data['permission_level'] = instance.permission_level
    

    return jsonify ({'instances':instance_data})


# Delete Instance By Instance ID
@app.route('/api/v1/instance/<instance_id>', methods=['DELETE'])
def delete_instance(instance_id):

    instance = Instance.query.filter_by(instance_id=instance_id).first()

    if not instance:
        return jsonify ({'message':'No Instance Found!'})
    
    db.session.delete(instance)
    db.session.commit()

    return jsonify ({'message':'Instance Deleted Successfully!'})






"""     Teams Api Methods     """

# List All Teams
@app.route('/api/v1/allteams', methods=['GET'])
def get_all_teams_with_members():

    teams = Teams.query.all()
    output = []

    for team in teams:
        team_data = {}
        team_data['team_id'] = team.team_id
        team_data['team_name'] = team.team_name
        team_data['owner'] = team.owner
        team_data['instance_id'] = team.instance_id
        team_data['modules_owned'] = team.modules_owned
        output.append(team_data)

    members = Members.query.all()
    output = []

    for member in members:
        member_data = {}
        member_data['member_id'] = member.member_id
        member_data['member_name'] = member.member_name
        member_data['email'] = member.email
        member_data['team_id'] = member.team_id
        member_data['member_role'] = member.role
        member_data['permission_level'] = member.permission_level
        output.append(member_data)

    return jsonify ({'teams':output},{'members':output})


# Create A Team 
@app.route('/api/v1/team', methods=['POST'])
def create_team():

    data = request.get_json()
    new_team = Teams(team_id = data['team_id'],team_name = data['team_name'],owner = data['owner'],instance_id = data['instance_id'],modules_owned = data['modules_owned'] )
    db.session.add(new_team)
    db.session.commit()

    return jsonify({'message':'New Team Created'})

# View A Team
@app.route('/api/v1/team/<team_id>', methods=['GET'])
def get_one_team(team_id):

    team = Teams.query.filter_by(team_id=team_id).first()

    if not team:
        return jsonify ({'message':'No Team Found!'})
    team_data = {}
    team_data['team_id'] = team.team_id
    team_data['team_name'] = team.team_name
    team_data['owner'] = team.owner
    team_data['instance_id'] = team.instance_id
    team_data['modules_owned'] = team.modules_owned

    members = Members.query.filter_by(team_id=team_id).all()
    output = []

    for member in members:
        member_data = {}
        member_data['member_id'] = member.member_id
        member_data['member_name'] = member.member_name
        member_data['email'] = member.email
        member_data['team_id'] = member.team_id
        member_data['member_role'] = member.role
        member_data['permission_level'] = member.permission_level
        output.append(member_data)

    return jsonify ({'team':team_data},{'members':output})


# Add Member For Team
@app.route('/api/v1/team/<team_id>/member', methods=['POST'])
def create_member_to_team(team_id):

    team_id=team_id
    data = request.get_json()
    new_member = Members(member_id=data['member_id'], member_name=data['member_name'],email= data['email'],team_id=data['team_id'],role=data['role'],permission_level= data['permission_level'])
    db.session.add(new_member)
    db.session.commit()

    return jsonify({'message':'New Member Created'})

# Delete A Member From Team
@app.route('/api/v1/team/<team_id>/<member_id>', methods=['DELETE'])
def delete_member_from_team(team_id,member_id):

    team_id=team_id
    member = Members.query.filter_by(member_id=member_id).first()

    if not member:
        return jsonify ({'message':'No Member Found!'})
    
    db.session.delete(member)
    db.session.commit()

    return jsonify ({'message':'Member Deleted Successfully!'})

# List All Members
@app.route('/api/v1/members', methods=['GET'])
def get_all_members():

    members = Members.query.all()
    output = []

    for member in members:
        member_data = {}
        member_data['member_id'] = member.member_id
        member_data['member_name'] = member.member_name
        member_data['email'] = member.email
        member_data['team_id'] = member.team_id
        member_data['member_role'] = member.role
        member_data['permission_level'] = member.permission_level
        output.append(member_data)

    return jsonify ({'members':output})



if __name__ == '__main__':
    app.run(debug=True)



    