import React from 'react';
import { List, Card, Typography, Tag } from 'antd';
import moment from 'moment';

const { Text, Title, Paragraph } = Typography;

const MedicationReminders = ({ userId, dueMedications }) => {
    if (!dueMedications || dueMedications.length === 0) {
        return (
            <Card title="Upcoming Reminders">
                <Text>No medications due soon.</Text>
            </Card>
        );
    }

    // Function to determine the next reminder time for today
    const getNextReminderForToday = (reminderTimes) => {
        if (!reminderTimes || reminderTimes.length === 0) return null;
        
        const now = moment();
        const sortedTimes = reminderTimes
            .map(t => moment(t, 'HH:mm'))
            .filter(mt => mt.isValid()) // Ensure time is valid
            .sort((a, b) => a.diff(b)); // Sort times

        for (let rt of sortedTimes) {
            if (rt.isAfter(now)) {
                return rt.format('HH:mm'); // Return the first reminder time that is after current time
            }
        }
        return null; // No upcoming reminders for today
    };

    return (
        <Card title="Upcoming Reminders" style={{ marginBottom: '20px' }}>
            <List
                itemLayout="horizontal"
                dataSource={dueMedications}
                renderItem={med => {
                    const nextDoseToday = getNextReminderForToday(med.reminder_times);
                    return (
                        <List.Item>
                            <List.Item.Meta
                                title={<Text strong>{med.medication_name}{nextDoseToday ? <Tag color="blue" style={{ marginLeft: 8}}>{`Next: ${nextDoseToday}`}</Tag> : <Tag color="gold" style={{ marginLeft: 8}}>Check Schedule</Tag>}</Text>}
                                description={
                                    <>
                                        {med.dosage && <Text>Dosage: {med.dosage} <br /></Text>}
                                        {med.frequency && <Text>Frequency: {med.frequency} <br /></Text>}
                                        {!nextDoseToday && med.reminder_times && med.reminder_times.length > 0 && (
                                            <Text type="secondary">Scheduled times: {med.reminder_times.join(', ')}</Text>
                                        )}
                                    </>
                                }
                            />
                        </List.Item>
                    );
                }}
            />
        </Card>
    );
};

export default MedicationReminders;
```
