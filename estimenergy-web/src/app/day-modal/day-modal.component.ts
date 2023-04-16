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
import { DayCreate } from '../api';
import { formatDate } from '@angular/common';

@Component({
  selector: 'app-day-modal',
  templateUrl: './day-modal.component.html',
  styleUrls: ['./day-modal.component.css'],
})
export class DayModalComponent {
  @ViewChild('content', { static: false }) content!: TemplateRef<any>;
  @Input() device: string = '';
  @Input() modalTitle: string = '';
  @Input() dayCreate!: DayCreate;
  @Output() save: EventEmitter<DayCreate> = new EventEmitter<DayCreate>();
  @Output() abort: EventEmitter<void> = new EventEmitter<void>();

  selectedDate!: NgbDateStruct;


  constructor(private calendar: NgbCalendar) { }

  ngOnInit() {
    // Assign default values if no dayCreate is given
    if (!this.dayCreate) {
      this.dayCreate = {
        device_name: this.device,
        date: '1970-01-01',
        energy: 0,
        accuracy: 1,
      };
    }
    this.selectedDate = this.calendar.getToday();
  }

  onSaveClick() {
    this.dayCreate.date = this.dateToString(this.selectedDate);
    this.save.emit(this.dayCreate);
  }

  onAbortClick() {
    this.abort.emit();
  }

  dateToString(date: NgbDateStruct): string {
    const dateObj = new Date(date.year, date.month, date.day);
    return formatDate(dateObj, 'yyyy-MM-dd', 'en-US');
  }
}
