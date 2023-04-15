import { Component } from '@angular/core';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { DayCreate, DayRead, DayService } from '../api';
import { DayModalComponent } from '../day-modal/day-modal.component';

@Component({
  selector: 'app-energy-table',
  templateUrl: './energy-table.component.html',
  styleUrls: ['./energy-table.component.css'],
})
export class EnergyTableComponent {
  days: DayRead[] = [];

  constructor(private dayService: DayService, private modalService: NgbModal) {
    this.dayService = dayService;
    this.modalService = modalService;
  }

  ngOnInit(): void {
    this.updateDays();
  }

  updateDays() {
    this.dayService.getDaysDayGet().subscribe((days: DayRead[]) => {
      this.days = days;
    });
  }

  onCreateClick() {
    const modalRef = this.modalService.open(DayModalComponent);
    modalRef.componentInstance.modalTitle = 'Create Day';
    modalRef.componentInstance.device = 'glow';

    modalRef.componentInstance.save.subscribe((dayCreate: DayCreate) => {
      console.log(dayCreate);
      this.dayService
        .createDayDayPost(dayCreate)
        .subscribe((day: DayRead) => {});
      modalRef.close();
      this.updateDays();
    });

    modalRef.componentInstance.abort.subscribe(() => {
      modalRef.close();
    });
  }
}
