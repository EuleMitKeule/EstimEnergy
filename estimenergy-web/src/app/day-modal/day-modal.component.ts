import {
  Component,
  EventEmitter,
  Input,
  Output,
  TemplateRef,
  ViewChild,
} from '@angular/core';
import {
  NgbCalendar,
  NgbDate,
  NgbDateStruct,
} from '@ng-bootstrap/ng-bootstrap';
import { DayCreate, DeviceConfigRead } from '../api';
import { formatDate } from '@angular/common';

@Component({
  selector: 'app-day-modal',
  templateUrl: './day-modal.component.html',
  styleUrls: ['./day-modal.component.css'],
})
export class DayModalComponent {
  @ViewChild('content', { static: false }) content!: TemplateRef<any>;
  @Input() devices: DeviceConfigRead[] = [];
  @Input() modalTitle: string = '';
  @Input() dayCreate!: DayCreate;
  @Output() save: EventEmitter<DayCreate> = new EventEmitter<DayCreate>();
  @Output() abort: EventEmitter<void> = new EventEmitter<void>();

  selectedDate: NgbDateStruct = this.calendar.getToday();

  constructor(private calendar: NgbCalendar) { }

  ngOnInit() {
    if (!this.dayCreate) {
      this.dayCreate = {
        device_name: '',
        date: '1970-01-01',
        energy: 0,
        accuracy: 1,
      };
    }

    if (!this.dayCreate.date) {
      this.selectedDate = this.calendar.getToday();
    }
    else {
      this.selectedDate = this.stringToDate(this.dayCreate.date);
    }
  }

  onSubmit() {
    this.dayCreate.date = this.dateToString(this.selectedDate);
    this.save.emit(this.dayCreate);
  }

  onAbortClick() {
    this.abort.emit();
  }

  onSelectDevice(device: DeviceConfigRead) {
    this.dayCreate.device_name = device.name;
  }

  dateToString(date: NgbDateStruct): string {
    const dateObj = new Date(date.year, date.month - 1, date.day);
    const dateStr = formatDate(dateObj, 'yyyy-MM-dd', 'en-US');
    return dateStr;
  }

  stringToDate(dateStr: string): NgbDateStruct {
    const dateObj = new Date(dateStr);
    const date = new NgbDate(dateObj.getFullYear(), dateObj.getMonth() + 1, dateObj.getDate());
    return date;
  }
}
