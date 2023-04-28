import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { DeviceConfig } from '../api';
import { AbstractControl, FormBuilder, FormGroup, Validators } from '@angular/forms';


@Component({
  selector: 'app-device-modal',
  templateUrl: './device-modal.component.html',
  styleUrls: ['./device-modal.component.css']
})
export class DeviceModalComponent implements OnInit {
  DEVICE_TYPES: string[] = [
    "glow",
  ];

  @Input() modalTitle: string = '';
  @Input() deviceConfig!: DeviceConfig;
  @Output() save: EventEmitter<DeviceConfig> = new EventEmitter<DeviceConfig>();
  @Output() abort: EventEmitter<void> = new EventEmitter<void>();

  constructor() { }

  ngOnInit(): void {
  }

  onSubmit() {
    this.save.emit(this.deviceConfig);
  }

  onAbortClick() {
    this.abort.emit();
  }
}
