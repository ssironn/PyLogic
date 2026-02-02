"""CLI commands for the application."""
import click
from flask.cli import with_appcontext
from sqlalchemy import select
from werkzeug.security import generate_password_hash

from app.extensions import db
from models import Admin, MathArea, MathSubarea


@click.command('seed-admin')
@with_appcontext
def seed_admin_command():
    """Create default admin user if it doesn't exist."""
    email = 'admin@email.com'

    # Check if admin already exists
    stmt = select(Admin).where(Admin.email == email)
    result = db.session.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        click.echo(f'Admin {email} already exists.')
        return

    # Create default admin
    admin = Admin(
        name='Administrator',
        email=email,
        password_hash=generate_password_hash('admin'),
        active=True
    )

    db.session.add(admin)
    db.session.commit()

    click.echo(f'Default admin created: {email} / admin')


@click.command('create-admin')
@click.option('--name', prompt='Admin name', help='Name of the admin')
@click.option('--email', prompt='Email', help='Email of the admin')
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True, help='Password')
@with_appcontext
def create_admin_command(name, email, password):
    """Create a new admin user."""
    # Check if email already exists
    stmt = select(Admin).where(Admin.email == email)
    result = db.session.execute(stmt)
    existing = result.scalar_one_or_none()

    if existing:
        click.echo(f'Error: Admin with email {email} already exists.')
        return

    # Create admin
    admin = Admin(
        name=name,
        email=email,
        password_hash=generate_password_hash(password),
        active=True
    )

    db.session.add(admin)
    db.session.commit()

    click.echo(f'Admin created: {email}')


@click.command('seed-math-areas')
@with_appcontext
def seed_math_areas_command():
    """Seed mathematical areas and subareas."""
    # Define areas and their subareas
    areas_data = [
        {
            'name': 'Algebra',
            'description': 'Estudo de estruturas algebricas e operacoes',
            'color': '#6366f1',
            'order': 1,
            'subareas': [
                {'name': 'Algebra Linear', 'order': 1},
                {'name': 'Algebra Abstrata', 'order': 2},
                {'name': 'Polinomios', 'order': 3},
                {'name': 'Equacoes e Inequacoes', 'order': 4},
            ]
        },
        {
            'name': 'Geometria',
            'description': 'Estudo das formas, tamanhos e propriedades do espaco',
            'color': '#22c55e',
            'order': 2,
            'subareas': [
                {'name': 'Geometria Plana', 'order': 1},
                {'name': 'Geometria Espacial', 'order': 2},
                {'name': 'Geometria Analitica', 'order': 3},
                {'name': 'Geometria Nao-Euclidiana', 'order': 4},
            ]
        },
        {
            'name': 'Calculo',
            'description': 'Estudo de limites, derivadas e integrais',
            'color': '#f59e0b',
            'order': 3,
            'subareas': [
                {'name': 'Limites', 'order': 1},
                {'name': 'Derivadas', 'order': 2},
                {'name': 'Integrais', 'order': 3},
                {'name': 'Calculo Vetorial', 'order': 4},
                {'name': 'Equacoes Diferenciais', 'order': 5},
            ]
        },
        {
            'name': 'Estatistica',
            'description': 'Coleta, analise e interpretacao de dados',
            'color': '#3b82f6',
            'order': 4,
            'subareas': [
                {'name': 'Estatistica Descritiva', 'order': 1},
                {'name': 'Probabilidade', 'order': 2},
                {'name': 'Inferencia Estatistica', 'order': 3},
                {'name': 'Distribuicoes', 'order': 4},
            ]
        },
        {
            'name': 'Logica Matematica',
            'description': 'Estudo da estrutura formal do raciocinio',
            'color': '#8b5cf6',
            'order': 5,
            'subareas': [
                {'name': 'Logica Proposicional', 'order': 1},
                {'name': 'Logica de Predicados', 'order': 2},
                {'name': 'Teoria dos Conjuntos', 'order': 3},
                {'name': 'Demonstracoes', 'order': 4},
            ]
        },
        {
            'name': 'Aritmetica',
            'description': 'Estudo dos numeros e operacoes basicas',
            'color': '#ef4444',
            'order': 6,
            'subareas': [
                {'name': 'Numeros Inteiros', 'order': 1},
                {'name': 'Numeros Racionais', 'order': 2},
                {'name': 'Numeros Reais', 'order': 3},
                {'name': 'Divisibilidade', 'order': 4},
                {'name': 'Numeros Primos', 'order': 5},
            ]
        },
        {
            'name': 'Trigonometria',
            'description': 'Estudo das relacoes entre lados e angulos de triangulos',
            'color': '#14b8a6',
            'order': 7,
            'subareas': [
                {'name': 'Funcoes Trigonometricas', 'order': 1},
                {'name': 'Identidades Trigonometricas', 'order': 2},
                {'name': 'Equacoes Trigonometricas', 'order': 3},
                {'name': 'Trigonometria no Triangulo', 'order': 4},
            ]
        },
        {
            'name': 'Analise Combinatoria',
            'description': 'Estudo de contagem e arranjos',
            'color': '#ec4899',
            'order': 8,
            'subareas': [
                {'name': 'Principio Fundamental da Contagem', 'order': 1},
                {'name': 'Permutacoes', 'order': 2},
                {'name': 'Combinacoes', 'order': 3},
                {'name': 'Arranjos', 'order': 4},
            ]
        },
    ]

    areas_created = 0
    subareas_created = 0

    for area_data in areas_data:
        subareas_list = area_data.pop('subareas')

        # Check if area already exists
        stmt = select(MathArea).where(MathArea.name == area_data['name'])
        result = db.session.execute(stmt)
        area = result.scalar_one_or_none()

        if not area:
            area = MathArea(**area_data)
            db.session.add(area)
            db.session.flush()  # Get the ID
            areas_created += 1
            click.echo(f'Created area: {area.name}')

        # Create subareas
        for subarea_data in subareas_list:
            stmt = select(MathSubarea).where(
                MathSubarea.math_area_id == area.id,
                MathSubarea.name == subarea_data['name']
            )
            result = db.session.execute(stmt)
            existing_subarea = result.scalar_one_or_none()

            if not existing_subarea:
                subarea = MathSubarea(
                    math_area_id=area.id,
                    **subarea_data
                )
                db.session.add(subarea)
                subareas_created += 1

    db.session.commit()

    click.echo(f'Seeding complete: {areas_created} areas, {subareas_created} subareas created.')


def register_commands(app):
    """Register CLI commands with the app."""
    app.cli.add_command(seed_admin_command)
    app.cli.add_command(create_admin_command)
    app.cli.add_command(seed_math_areas_command)
