import datetime as dt
from sqlalchemy import String, Integer, Boolean, DateTime, Date, Time
from sqlalchemy.orm import  mapped_column, Mapped
from .database import db


class Appointment(db.Model):
    __tablename__ = 'agenda'
    id:Mapped[int] = mapped_column(Integer, primary_key=True)

    reason:Mapped[str] = mapped_column(String(128), nullable=True)
    status:Mapped[bool] = mapped_column(Boolean, default=True)
    dt_start:Mapped[dt.datetime] = mapped_column(DateTime)
    dt_end:Mapped[dt.datetime] = mapped_column(DateTime)
    id_patient:Mapped[int] = mapped_column(Integer)
    id_doctor:Mapped[int] = mapped_column(Integer)
    id_clinic:Mapped[int] = mapped_column(Integer)
    id_user:Mapped[int] = mapped_column(Integer)

    def to_dict(self):
        return {
            'id': self.id,
            'date': self.dt_start.date(),
            'start': self.dt_start.time(),
            'duration_minutes': int((self.dt_end-self.dt_start).seconds/60), # arrodoniment a minuts
            'status': self.status
        }
    
    def from_json(self,json_data)->bool:
        try:
            self.reason = json_data.get('reason')
            
            # converteixo dia, hora i duració a format datetime

            temp_date= dt.date.fromisoformat(json_data.get('date'))
            temp_start = dt.time.fromisoformat(json_data.get('start'))
            temp_start = dt.time(temp_start.hour, int(temp_start.minute /15)*15,0) # arrodoniment a 15minuts
            temp_duration = int(json_data.get('duration_minutes'))*15 #arrodoniment a 15min
            self.dt_start=dt.datetime(temp_date.year,temp_date.month,temp_date.day,temp_start.hour,temp_start.minute,0)
            self.dt_end = self.dt_start + dt.timedelta(minutes=temp_duration)

            self.id_patient=json_data.get('patient_id')
            self.id_doctor = json_data.get('doctor_id')
            self.id_clinic = json_data.get('clinic_id')
            self.id_user = json_data.get('user_id')
        except Exception as e:
            return False
        else:
            return True
        
    def to_json(self)->dict:
        return {
            'id': self.id,
            'patient_id': self.id_patient,
            'reason': self.reason,
            'date': self.dt_start.date().isoformat(), 
            'duration_minutes': (self.dt_end - self.dt_start).seconds/60

        }

    @property
    def date(self):
        return self.dt_start.date()
    @date.setter
    def date(self,date_string:str):
        newdate = dt.date.fromisoformat(date_string)
        self.dt_start.replace(year=newdate.year,month=newdate.month, day=newdate.day)
        self.dt_end.replace(year=newdate.year,month=newdate.month, day=newdate.day)


    @property
    def timeslot(self):
        return self.dt_start.time(), self.dt_end.time()
    @timeslot.setter
    def timeslot(self,start_time:str, duration:int=15, rounding_val =15):
        # crea un temps inici i final, arrodonit a blocs de 15 minuts
        
        new_time = dt.time.fromisoformat(start_time)
        new_start_minute = int(newtime.minute/rounding_val)*rounding_val
        new_duration = int(duration/rounding_val) * rounding_val

        self.dt_start.replace(hour= new_time.hour, minute=new_start_minute,second=0)
        self.dt_end = self.dt_start + dt.timedelta(minutes=new_duration)