"""
SLA Calculator
==============

Calcula fechas de vencimiento para SLA semanal y mensual.
Timezone: America/Santiago
"""

from datetime import datetime, date, timedelta
from typing import Optional, Tuple
import calendar

try:
    import pytz
    TIMEZONE = pytz.timezone("America/Santiago")
except ImportError:
    TIMEZONE = None
    print("⚠️ pytz no instalado, usando UTC")


def now_chile() -> datetime:
    """Retorna datetime actual en Chile."""
    if TIMEZONE:
        return datetime.now(TIMEZONE)
    return datetime.now()


def today_chile() -> date:
    """Retorna fecha actual en Chile."""
    return now_chile().date()


def get_week_bounds(ref_date: date) -> Tuple[date, date]:
    """
    Obtiene inicio y fin de la semana operacional.
    
    Semana operacional:
    - Inicio: Lunes 00:00
    - Fin: Viernes 18:00 (conceptual, retornamos viernes)
    
    Args:
        ref_date: Fecha de referencia
    
    Returns:
        (lunes, viernes) de la semana
    """
    # Encontrar el lunes de esta semana
    days_since_monday = ref_date.weekday()  # 0=lunes
    monday = ref_date - timedelta(days=days_since_monday)
    friday = monday + timedelta(days=4)
    
    return monday, friday


def get_next_wednesday_18h(ref_date: date) -> datetime:
    """
    Calcula el miércoles siguiente a las 18:00.
    
    Usado para SLA semanal: deadline es miércoles T+1 a las 18:00.
    
    Args:
        ref_date: Fecha de referencia (típicamente el viernes de la semana T)
    
    Returns:
        datetime del miércoles siguiente a las 18:00
    """
    # Días hasta el próximo miércoles
    days_until_wednesday = (2 - ref_date.weekday()) % 7
    if days_until_wednesday == 0:
        days_until_wednesday = 7  # Si es miércoles, ir al siguiente
    
    next_wednesday = ref_date + timedelta(days=days_until_wednesday)
    
    # Agregar hora 18:00
    if TIMEZONE:
        return TIMEZONE.localize(datetime.combine(next_wednesday, datetime.min.time().replace(hour=18)))
    return datetime.combine(next_wednesday, datetime.min.time().replace(hour=18))


def get_last_day_of_month(year: int, month: int) -> date:
    """Retorna el último día del mes."""
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, last_day)


def is_business_day_simple(d: date) -> bool:
    """
    Determina si es día hábil (lunes a viernes).
    Fallback simple sin usar business_calendar_cl.
    """
    return d.weekday() < 5  # 0-4 = lunes a viernes


def add_business_days(start_date: date, days: int, calendar_data: list = None) -> date:
    """
    Agrega N días hábiles a una fecha.
    
    Args:
        start_date: Fecha inicial
        days: Número de días hábiles a agregar
        calendar_data: Lista de dicts con {day, is_business_day} (opcional)
    
    Returns:
        Fecha resultante
    """
    # Crear lookup de calendario si está disponible
    calendar_lookup = {}
    if calendar_data:
        for row in calendar_data:
            day_str = str(row.get("day", ""))[:10]
            is_bd = row.get("is_business_day", True)
            calendar_lookup[day_str] = is_bd
    
    current = start_date
    added = 0
    
    while added < days:
        current = current + timedelta(days=1)
        
        # Verificar si es día hábil
        day_str = current.isoformat()
        if day_str in calendar_lookup:
            is_bd = calendar_lookup[day_str]
        else:
            is_bd = is_business_day_simple(current)
        
        if is_bd:
            added += 1
    
    return current


def get_sla_semanal_deadline(week_friday: date) -> datetime:
    """
    Calcula deadline de SLA semanal.
    
    Regla: Miércoles de la semana siguiente (T+1) a las 18:00.
    
    Args:
        week_friday: Viernes de la semana T
    
    Returns:
        datetime del deadline
    """
    return get_next_wednesday_18h(week_friday)


def get_sla_mensual_deadline(year: int, month: int, calendar_data: list = None) -> datetime:
    """
    Calcula deadline de SLA mensual.
    
    Regla: 3 días hábiles después del último día del mes, a las 18:00.
    
    Args:
        year: Año
        month: Mes
        calendar_data: Datos del calendario de días hábiles
    
    Returns:
        datetime del deadline
    """
    last_day = get_last_day_of_month(year, month)
    deadline_date = add_business_days(last_day, 3, calendar_data)
    
    if TIMEZONE:
        return TIMEZONE.localize(datetime.combine(deadline_date, datetime.min.time().replace(hour=18)))
    return datetime.combine(deadline_date, datetime.min.time().replace(hour=18))


def get_period_code_weekly(week_friday: date) -> str:
    """
    Genera código de período para SLA semanal.
    Formato: YYYY-WNN (año-semana ISO)
    """
    year, week, _ = week_friday.isocalendar()
    return f"{year}-W{week:02d}"


def get_period_code_monthly(year: int, month: int) -> str:
    """
    Genera código de período para SLA mensual.
    Formato: YYYY-MM
    """
    return f"{year}-{month:02d}"
