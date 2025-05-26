import React, { useState, useEffect } from 'react';
import { Form, Input, Button, DatePicker, TimePicker, Space, InputNumber } from 'antd';
import moment from 'moment';

const MedicationForm = ({ userId, medicationToEdit, onSave, onCancel }) => {
    const [form] = Form.useForm();
    const isEditing = !!medicationToEdit;

    useEffect(() => {
        if (isEditing && medicationToEdit) {
            form.setFieldsValue({
                medication_name: medicationToEdit.medication_name,
                dosage: medicationToEdit.dosage,
                frequency: medicationToEdit.frequency,
                start_date: medicationToEdit.start_date ? moment(medicationToEdit.start_date) : null,
                end_date: medicationToEdit.end_date ? moment(medicationToEdit.end_date) : null,
                // reminder_times are stored as HH:MM strings in the backend model
                // For the form, we'll handle them as an array of moment objects if using TimePicker multiple times
                // Or, if it's a single text input for comma-separated values:
                reminder_times_str: medicationToEdit.reminder_times ? medicationToEdit.reminder_times.join(',') : '',
                notes: medicationToEdit.notes,
            });
        } else {
            form.resetFields();
        }
    }, [medicationToEdit, form, isEditing]);

    const handleFinish = async (values) => {
        const payload = {
            ...values,
            user_id: userId,
            start_date: values.start_date ? values.start_date.format('YYYY-MM-DD') : null,
            end_date: values.end_date ? values.end_date.format('YYYY-MM-DD') : null,
            // Convert comma-separated string to array of HH:MM strings
            reminder_times: values.reminder_times_str 
                            ? values.reminder_times_str.split(',').map(t => t.trim()).filter(t => t) 
                            : [],
        };
        // Remove the temporary string field
        delete payload.reminder_times_str;


        if (!payload.start_date) {
            form.setFields([{ name: 'start_date', errors: ['Start date is required.'] }]);
            return;
        }
        
        // Basic validation for reminder times format (HH:MM)
        if (payload.reminder_times.length > 0) {
            const timeRegex = /^([01]\d|2[0-3]):([0-5]\d)$/;
            for (const timeStr of payload.reminder_times) {
                if (!timeRegex.test(timeStr)) {
                    form.setFields([{ name: 'reminder_times_str', errors: [`Invalid time format: ${timeStr}. Use HH:MM.`] }]);
                    return;
                }
            }
        }

        onSave(payload, isEditing ? medicationToEdit._id : null);
    };

    return (
        <Form
            form={form}
            layout="vertical"
            onFinish={handleFinish}
            initialValues={{
                // Default values can be set here if needed
                medication_name: '',
                dosage: '',
                frequency: '',
                start_date: null, // moment() for today by default?
                end_date: null,
                reminder_times_str: '',
                notes: '',
            }}
        >
            <Form.Item
                name="medication_name"
                label="Medication Name"
                rules={[{ required: true, message: 'Please input the medication name!' }]}
            >
                <Input />
            </Form.Item>
            <Form.Item name="dosage" label="Dosage (e.g., 1 tablet, 10mg)">
                <Input />
            </Form.Item>
            <Form.Item name="frequency" label="Frequency (e.g., once a day, every 6 hours)">
                <Input />
            </Form.Item>
            <Form.Item
                name="start_date"
                label="Start Date"
                rules={[{ required: true, message: 'Please select the start date!' }]}
            >
                <DatePicker format="YYYY-MM-DD" style={{ width: '100%' }}/>
            </Form.Item>
            <Form.Item name="end_date" label="End Date (Optional)">
                <DatePicker format="YYYY-MM-DD" style={{ width: '100%' }}/>
            </Form.Item>
            <Form.Item 
                name="reminder_times_str" 
                label="Reminder Times (Optional, HH:MM, comma-separated, e.g., 08:00,20:00)"
                tooltip="Enter times in HH:MM format separated by commas."
            >
                <Input placeholder="08:00,14:00,20:00" />
            </Form.Item>
            <Form.Item name="notes" label="Notes (Optional)">
                <Input.TextArea rows={3} />
            </Form.Item>
            <Form.Item>
                <Space>
                    <Button type="primary" htmlType="submit">
                        {isEditing ? 'Save Changes' : 'Add Medication'}
                    </Button>
                    {onCancel && (
                        <Button onClick={onCancel}>
                            Cancel
                        </Button>
                    )}
                </Space>
            </Form.Item>
        </Form>
    );
};

export default MedicationForm;
```
