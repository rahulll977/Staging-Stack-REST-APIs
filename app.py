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
    

class Teams(db.Model):
    team_id = db.Column(db.Integer, primary_key=True)
    team_name = db.Column(db.String(250))
    owner = db.Column(db.String(250))
    instances = db.Column(db.String(500))
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

@app.route('/api/v1/deploy/instances/<instance_id>', methods=['POST'])
def deploy_instances(instance_id):
    data = request.get_json()
    
    new_deploy = Deploy(member_id = data['user_id'],branch = data['branch'],reason = data['reason'])
    member = Members.query.filter_by(member_id = new_deploy.member_id).first()
    db.session.add(new_deploy)
    db.session.commit()
    deploy_data = {}
    deploy_data['user_name'] = member.member_name
    deploy_data['branch']= new_deploy.branch
    deploy_data['reason']= new_deploy.reason
    return jsonify({'deploy': deploy_data})




# List All Teams
@app.route('/api/v1/teams', methods=['GET'])
def get_all_teams_():

    teams = Teams.query.all()
    
    output = []
    

    for team in teams:
        team_data = {}
        
        team_data['team_name'] = team.team_name
        
        team_data['team_id'] = team.team_id
        output.append(team_data)

    return jsonify ({'teams': output})


# List Instances By Team
@app.route('/api/v1/instances/teams/<team_id>', methods=['GET'])
def get_all_instances(team_id):
    instances = Instance.query.filter_by(team_id=team_id).all()
    member = Members.query.filter_by(team_id=team_id).all()
    deploy = Deploy.query.filter_by(member_id = member.member_id).all()
    output = []
    for instance in instances:
        instance_data = {}
        instance_data['instance_id'] = instance.instance_id
        instance_data['instance_name'] = instance.instance_name
        instance_data[''] = instance.usage_type
        instance_data['team_id'] = instance.team_id
        instance_data['status'] = instance.status
        output.append(instance_data)

    return jsonify ({'instances':output})

#Create Instance For Team
@app.route('/api/v1/instances/teams/<team_id>', methods=['POST'])
def create_instance_for_team(team_id):
    data = request.get_json()
    new_instance = Instance(instance_name = data['instance_name'], usage_type = data['usage_type'], team_id = team_id, status = data['state'])
    db.session.add(new_instance)
    db.session.commit()
    instance_data = {}
    instance_data['instance_id'] = new_instance.instance_id
    instance_data['instance_name'] = new_instance.instance_name
    instance_data['usage_type'] = new_instance.usage_type
    instance_data['team_id'] = new_instance.team_id
    instance_data['state'] = new_instance.status

    return jsonify({'instance':instance_data})

# View Instance By Instance ID
@app.route('/api/v1/instances/<instance_id>', methods=['GET'])
def get_one_instance(instance_id):

    instance = Instance.query.filter_by(instance_id=instance_id).first()
    team_id = instance.team_id
    team = Teams.query.filter_by(team_id=team_id).first() 

    if not instance:
        return jsonify ({'message':'No Instance Found!'})
    instance_data = {}
    instance_data['instance_id'] = instance.instance_id
    instance_data['instance_name'] = instance.instance_name
    instance_data['team_name'] = team.team_name
    
    

    return jsonify ({'instances':instance_data})


# Delete Instance By Instance ID
@app.route('/api/v1/instances/<instance_id>', methods=['DELETE'])
def delete_instance(instance_id):

    instance = Instance.query.filter_by(instance_id=instance_id).first()

    if not instance:
        return jsonify ({'message':'No Instance Found!'})
    
    db.session.delete(instance)
    db.session.commit()

    return None



"""     Teams Api Methods     """

# List All Teams With Members

@app.route('/api/v1/teams/all', methods=['GET'])
def get_all_teams_with_members():
    te = Teams.query.all()
    x = []
    for i in te:
        x.append(i.team_id)

    v = len(x)
    
    output = []
    for n in range(1,v+1):
        instances = Instance.query.filter_by(team_id=n).all()
        teams = Teams.query.filter_by(team_id=n).all()
        members = Members.query.filter_by(team_id=n).all()
        output_ = []
        output_1 = []
        for instance in instances:
            instance_data = {}
            instance_data['instance_id'] = instance.instance_id
            instance_data['instance_name'] = instance.instance_name
            instance_data['usage_type'] = instance.usage_type
            instance_data['team_id'] = n
            instance_data['state'] = instance.status
    
            output_.append(instance_data)

        for member in members:
            member_data = {}
            member_data['member_name'] = member.member_name
            member_data['email'] = member.email
            member_data['member_role'] = member.role
            member_data['permission_level'] = member.permission_level
            output_1.append(member_data)
            
        for team in teams:
            team_data = {}
            team_data['team_id'] = n
            team_data['team_name'] = team.team_name
            team_data['owner'] = team.owner
            team_data['instances'] = output_
            team_data['modules_owned'] = team.modules_owned
            team_data['members'] = output_1
            output.append(team_data)
        output_ = []
        output_1 = []

    return jsonify ({'teams': output})


# Create A Team 
@app.route('/api/v1/teams', methods=['POST'])
def create_team():

    data = request.get_json()
    new_team = Teams(team_name = data['team_name'],owner = data['owner'],instances = data['instances'],modules_owned = data['modules_owned'])
    db.session.add(new_team)
    db.session.commit()
    team_data = {}
    team_data['team_name'] = data['team_name']
    team_data['owner'] = data['owner']
    team_data['instances'] = data['instances']
    team_data['modules_owned'] = data['modules_owned']
    team_data['team_id'] = new_team.team_id


    return jsonify({'team':team_data})

# View A Team
@app.route('/api/v1/teams/<team_id>', methods=['GET'])
def get_one_team(team_id):

    team = Teams.query.filter_by(team_id=team_id).first()
    instances = Instance.query.filter_by(team_id=team_id).all()
    members = Members.query.filter_by(team_id=team_id).all()
    output = []
    instance_ids = []
    for i in instances:
        instance_ids.append(i.instance_id)

    if not team:
        return jsonify ({'message':'No Team Found!'})

    for member in members:
        member_data = {}
        
        member_data['member_name'] = member.member_name
        member_data['email'] = member.email
        member_data['member_role'] = member.role
        member_data['permission_level'] = member.permission_level
        output.append(member_data)

    team_data = {}
    team_data['team_id'] = team.team_id
    team_data['team_name'] = team.team_name
    team_data['owner'] = team.owner
    team_data['instances'] = instance_ids
    team_data['modules_owned'] = team.modules_owned
    team_data['members'] = output
    
    
    return jsonify ({'team':team_data})


# Add Member For Team
@app.route('/api/v1/teams/<team_id>/member', methods=['POST'])
def create_member_to_team(team_id):

    
    data = request.get_json()
    new_member = Members( member_name=data['member_name'],email= data['email'],team_id = team_id,role=data['role'],permission_level= data['permission_level'])
    db.session.add(new_member)
    db.session.commit()
    member_data = {}
    member_data['member_name'] = new_member.member_name
    member_data['email'] = new_member.email
    member_data['role'] = new_member.role
    member_data['permission_level'] = new_member.permission_level
    member_data['member_id'] = new_member.member_id


    return jsonify({'member':member_data})

# Delete A Member From Team
@app.route('/api/v1/teams/<team_id>/<member_id>', methods=['DELETE'])
def delete_member_from_team(team_id,member_id):

    team_id=team_id
    member = Members.query.filter_by(member_id=member_id).first()

    if not member:
        return jsonify ({'message':'No Member Found!'})
    
    db.session.delete(member)
    db.session.commit()

    return None

""" 
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
"""

if __name__ == '__main__':
    app.run(debug=True)



    
