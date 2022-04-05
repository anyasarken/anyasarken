#!/usr/bin/env python3 
# -*- coding: utf-8 -*-
#----------------------------------------CODE INFO--------------------------------------------------------------------
# Created By    : yasar kenan
# Created Date  : 30.03.2022
# version       :'0.1'
#---------------------------------------------------------------------------------------------------------------------


# --------------------------------------USER GUIDE--------------------------------------------------------------------
# This software had been written to analyse and report hikvision and haikon
# DVR file systems. You can examine and see video file informations and you
# can export individual video files by using software.
#
# HOW TO USE
#   
#---------------------------------------------------------------------------------------------------------------------


# ---------------------------------------IMPORTS----------------------------------------------------------------------
import datetime 
# --------------------------------------------------------------------------------------------------------------------


#----------------------------------------CONSTANTS--------------------------------------------------------------------
# These constants are pointing master sectors byte adresses according to
# hikvision signature value which is {48 49 4b 56 49 53 49 4f 4e 40 48 41 4e 47 5a 48 4f 55}

diskSizeOffset = 56             #Offset for disk size.
systemLogsOffset = 80           #Offset for system logs area.
logSizeOffset = 88              #Offset for system logs size value.
videoAreaOffset = 104           #Offset for video area address.
dataBlockSizeOffset = 120       #Offset for size of one block. This value is generally 1GB.
totalDataBlocksOffset = 128     #Offset for total number of data block. This value changes according to disk size.
hikbtree1Offset = 136           #Offset for address of hikbtree structure copy 1.
hikbtree1SizeOffset = 144       #Offset for size of hikbtree structure copy 1.
hikbtree2Offset = 152           #Offset for address of hikbtree structure copy 2.
hikbtree2SizeOffset = 160       #Offset for size of hikbtree structure copy 2.
diskInitTimeOffset = 224        #Offset for disk initializaton time value.

#These constants are pointing Hikbtree header byte addresses acording to hikbtree signature
#which is {48 49 4b 42 54 52 45 45} Hikbtree position is recorded in master sector.

hikbtreeCreateTimeOffset = 44   #Offset for hikbtree creation time.
hikbtreeFooterOffset = 48       #Offset for hikbtree footer address.
pageListOffset = 64             #Offset for page list address. Page list keeps addresses of pages.
page1Offset = 72                #Offset for page 1 address recorded on hikbtree header file.
totalPageRecordNumber = 0       #Offset for total page numbers. This value can change according to disk size. 
pageAdresses = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]          #List will be used for keeping page addresses.
pageRecordNumbers = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]     #List will be used for keeping page record numbers.

#0: block address | 1: allocated flag | 2: channel | 3: start date time | 4: end date time
pageRecords = [[],[],[],[],[]]

with open('VIDEO_REPORT.TXT', 'a') as report:
    report.write('ID' + '\t|' + '    CHANNEL' +  '\t|\t' + '    START TIME' + '\t\t|\t' + '   END TIME' + '\t\t| ' + '  ALLOCATED' + '\t|\t' + '   ADDRESS' + '\n')


#---------------------------------------------------------------------------------------------------------------------


#-----------------------------------------FUNCTIONS-------------------------------------------------------------------

def read_8_from_offset(file, offset):
    file.seek(offset)
    return file.read(8)

def read_4_from_offset(file, offset):
    file.seek(offset)
    return file.read(4)

def add_report(text: str, value: int):
    with open('MASTER_SECTOR_REPORT.TXT', 'a') as report:
        report.write(text + ': ' + str(value) + '\n\n')

#This function writes first line to video report file.
def add_video_report(ID: int, channel: int, startTime: int, endTime: int, allocated: int, address: int):
    with open('VIDEO_REPORT.TXT', 'a') as report:
        report.write(str(ID) + '\t|\t' + str(channel) +  '\t|\t' + str(startTime) + '\t|\t' + str(endTime) + '\t|\t' + str(allocated) + '\t|\t' + str(address) + '\n')

#---------------------------------------------------------------------------------------------------------------------


#-------------------------------------MASTER SECTOR ANALYSE-----------------------------------------------------------
# open image file's first two sector including master sector in binary format and read only mode
with open('E:\hikvision_dolu_format_1\hikvision_dolu_format_1.001', 'rb', buffering=0) as imageFile:
    masterSector = (imageFile.read(1024))       
    signaturePosition = masterSector.find(b'\x48\x49\x4b\x56\x49\x53\x49\x4f\x4e\x40\x48\x41\x4e\x47\x5a\x48\x4f\x55')

    #if no signature has found then inform user.
    if(signaturePosition == -1):
        print("There is no hikvision signature on this image file!!!")

    #if hikvision (or haikon) signature has found then analyse master sector according to
    #offset values previously defined.
    else:
        #Total formatted disk size
        value = read_8_from_offset(imageFile, (signaturePosition + diskSizeOffset)) 
        diskSize = int.from_bytes(value, byteorder='little')
        add_report('Disk size', diskSize)

        #Address of system logs
        value = read_8_from_offset(imageFile, (signaturePosition + systemLogsOffset))
        systemLogsAddress = int.from_bytes(value, byteorder='little')
        add_report('Log address', systemLogsAddress)

        #Size of system logs
        value = read_8_from_offset(imageFile, (signaturePosition + logSizeOffset))
        systemLogsSize = int.from_bytes(value, byteorder='little')
        add_report('Log size', systemLogsSize)

        #Address of video data
        value = read_8_from_offset(imageFile, (signaturePosition + videoAreaOffset))
        videoAreaAddress = int.from_bytes(value, byteorder='little')
        add_report('Video address', videoAreaAddress)

        #Size of data block
        value = read_8_from_offset(imageFile, (signaturePosition + dataBlockSizeOffset))
        dataBlockSize = int.from_bytes(value, byteorder='little')
        add_report('Block size', dataBlockSize)

        #Number of total data blocks
        value = read_4_from_offset(imageFile, (signaturePosition + totalDataBlocksOffset))
        totalDataBlocks = int.from_bytes(value, byteorder='little')
        add_report('Number of data blocks', totalDataBlocks)

        #Address of hikbtree 1
        value = read_8_from_offset(imageFile, (signaturePosition + hikbtree1Offset))
        hikbtree1Address = int.from_bytes(value, byteorder='little')
        add_report('HIKBTREE 1 address', hikbtree1Address)

        #Size of hikbtree 1
        value = read_4_from_offset(imageFile, (signaturePosition + hikbtree1SizeOffset))
        hikbtree1Size = int.from_bytes(value, byteorder='little')
        add_report('HIKBTREE 1 size', hikbtree1Size)

        #Address of hikbtree 2
        value = read_8_from_offset(imageFile, (signaturePosition + hikbtree2Offset))
        hikbtree2Address = int.from_bytes(value, byteorder='little')
        add_report('HIKBTREE 2 address', hikbtree2Address)

        #Size of hikbtree 2
        value = read_4_from_offset(imageFile, (signaturePosition + hikbtree2SizeOffset))
        hikbtree2Size = int.from_bytes(value, byteorder='little')
        add_report('HIKBTREE 2 size', hikbtree2Size)

        #Date of disk initialization in UTC format
        value = read_4_from_offset(imageFile, (signaturePosition + diskInitTimeOffset))
        diskInitTime = int.from_bytes(value, byteorder='little')
        diskInitTime = datetime.datetime.fromtimestamp(diskInitTime)
        add_report('Disk initialization time (UTC)', diskInitTime)


#-------------------------------------HIKBTREE1 ANALYSE---------------------------------------------------------------

# open image file's first two sector including master sector in binary format and read only mode
with open('E:\hikvision_dolu_format_1\hikvision_dolu_format_1.001', 'rb', buffering=0) as imageFile:
    imageFile.seek(hikbtree1Address)
    hikbtree1File = (imageFile.read(hikbtree1Size))
    signaturePosition = hikbtree1File.find(b'\x48\x49\x4b\x42\x54\x52\x45\x45')

    
    #if no signature has found then inform user.
    if(signaturePosition == -1):
        print("There is no hikbtree signature on this image file!!!")

    else:
        #Hikbtree creation time
        value = read_4_from_offset(imageFile, (hikbtree1Address + signaturePosition + hikbtreeCreateTimeOffset)) 
        diskInitTime = int.from_bytes(value, byteorder='little')
        diskInitTime = datetime.datetime.fromtimestamp(diskInitTime)
        add_report('Hikbtree initialization time (UTC)', diskInitTime)

        #Hikbtree footer address
        value = read_8_from_offset(imageFile, (hikbtree1Address + signaturePosition + hikbtreeFooterOffset))
        hikbtree1FooterAddress = int.from_bytes(value, byteorder='little')
        add_report('HIKBTREE 1 footer address', hikbtree1FooterAddress)

        #Page list address
        value = read_8_from_offset(imageFile, (hikbtree1Address + signaturePosition + pageListOffset))
        pageListAddress = int.from_bytes(value, byteorder='little')
        add_report('Page list address', pageListAddress)

        #Total page number
        value = read_4_from_offset(imageFile, (pageListAddress))
        totalPageNumber = int.from_bytes(value, byteorder='little')
        add_report('Total page number on hikbtree', totalPageNumber)

        #All page adresses are being written to a list
        for i in range(totalPageNumber):
            value = read_8_from_offset(imageFile, (pageListAddress + 24 + (i*72)))
            pageAdresses[i] = int.from_bytes(value, byteorder='little')

        #Page addresses are being written to report
        for i in range(totalPageNumber):
            add_report('Page ' + str(i) + ' address: ', (pageAdresses[i]))

        #Total record numbers are being written to report and total number is calculated
        for i in range(totalPageNumber):
            value = read_4_from_offset(imageFile, (pageAdresses[i] + 16))
            pageRecordNumbers[i] = int.from_bytes(value, byteorder='little')
            add_report('Page ' + str(i) + ' record number: ', pageRecordNumbers[i])
            totalPageRecordNumber += pageRecordNumbers[i]

        
        for i in range(totalPageNumber):                                                    #This loop will be run for page number times
            for j in range(pageRecordNumbers[i]):                                           #This loop will be run for record numbers in every pages
                value = read_8_from_offset(imageFile, (pageAdresses[i] + 104 + j*48))       #Allocated or not section is reading
                if value == b'\xFF\xFF\xFF\xFF\xFF\xFF\xFF\xFF':                            #Page record is not allocated
                    allocatedFlag = 0
                if value == b'\x00\x00\x00\x00\x00\x00\x00\x00':
                    allocatedFlag = 1
                    
                value = read_4_from_offset(imageFile, (pageAdresses[i] + 113 + j*48))       #Channel information is reading
                value = int.from_bytes(value, byteorder='little')
                if(value > 256):
                    channel = 555
                else:
                    channel = value
                
                value = read_4_from_offset(imageFile, (pageAdresses[i] + 120 + j*48))       #Start time information is reading
                startDateTime = int.from_bytes(value, byteorder='little')              
                if(startDateTime != 2147483647):
                    startDateTime = startDateTime - 10800                                   #Time zone disabled. Looking for better solution.
                    startDateTime = datetime.datetime.fromtimestamp(startDateTime)
                else:
                    startDateTime = 1111111111111111111
                
                value = read_4_from_offset(imageFile, (pageAdresses[i] + 124 + j*48))       #End time information is reading
                endDateTime = int.from_bytes(value, byteorder='little')         
                if(endDateTime != 0):
                    endDateTime = endDateTime - 10800                                     #Time zone disabled. Looking for better solution.
                    endDateTime = datetime.datetime.fromtimestamp(endDateTime)
                else:
                    endDateTime = 1111111111111111111
                
                value = read_8_from_offset(imageFile, (pageAdresses[i] + 128 + j*48))       #Start time information is reading
                blockAddress = int.from_bytes(value, byteorder='little')
                
                pageRecords[0].append(blockAddress)
                pageRecords[1].append(allocatedFlag)
                pageRecords[2].append(channel)
                pageRecords[3].append(startDateTime)
                pageRecords[4].append(endDateTime)


        for i in range(totalPageRecordNumber):
            add_video_report(i, pageRecords[2][i], pageRecords[3][i], pageRecords[4][i], pageRecords[1][i], pageRecords[0][i])
