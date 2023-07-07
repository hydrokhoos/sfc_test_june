from typing import Optional
from ndn.app import NDNApp
from ndn.encoding import Name, InterestParam, BinaryStr, FormalName, MetaInfo, Component, ContentType

import subprocess
import sys
import time
from queue import Queue
from send_data import send_data


if len(sys.argv) <= 3:
    print(
        f'Bad call\nUsage: {sys.argv[0]} <service_name> <service_ip> <service_port>')
    exit(0)
service_name = Name.normalize(sys.argv[1])

q = Queue(maxsize=1)
SEGMENT_SIZE = 8000
FRESHNESS_PERIOD = 5.000
SERVICE_IP = str(sys.argv[2])
SERVICE_PORT = int(sys.argv[3])

app = NDNApp()


@app.route(service_name)
def on_interest(name: FormalName, param: InterestParam, _app_param: Optional[BinaryStr]):
    print(f'>> I: {Name.to_str(name)}, {param}')

    # parse interest name
    #   name: /func/content/32=metadata/v=1234567890987/seg=0
    #   name_noseg: /func/content/32=metadata/v=1234567890987
    #   name_nosegver: /func/content
    #   name_trim: /content
    #  or
    #   name: /func/content/v=1234567890987/seg=0
    #   name_noseg: /func/content/v=1234567890987
    #   name_nosegver: /func/content
    #   name_trim: /content
    if Component.get_type(name[-1]) == Component.TYPE_SEGMENT:
        seg_no = Component.to_number(name[-1])
        name_noseg = name[:-1]
    else:
        name_noseg = name
        seg_no = 0
    if Component.get_type(name_noseg[-1]) == Component.TYPE_VERSION:
        name_nosegver = name_noseg[:-1]
    else:
        name_nosegver = name_noseg
    if Name.to_str(name_nosegver[-1:]) == '/32=metadata':
        if seg_no >= 1:
            print('<< NACK ', {Name.to_str(name)})
            app.put_data(name, b'', content_type=ContentType.NACK)
            return
        name_nosegver = name_nosegver[:-1]
        name_trim = name_nosegver[1:]
    else:
        name_trim = name_noseg[1:]

    # get content
    holding_content = {'name': '', 'content': b'', 'time': 0.0}
    if not q.empty():
        holding_content = q.get()
    if Name.to_str(name_nosegver) == holding_content['name'] and \
            time.time() - holding_content['time'] <= FRESHNESS_PERIOD:
        processed_content = holding_content['content']
        q.put(holding_content)
    else:
        print(f'<< I: {Name.to_str(name_trim)} (ndncatchunks)')
        content = subprocess.run(
            ['ndncatchunks', Name.to_str(name_trim), '-qf'],
            capture_output=True
        ).stdout
        print(f'>> D: {Name.to_str(name_trim)} (ndncatchunks)')
        print()

        # service function
        print(f'To Service: {len(content)} bytes')
        t0_service = time.time()
        processed_content = send_data(SERVICE_IP, SERVICE_PORT, content)
        dt_service = time.time() - t0_service
        print(f'From Service: {len(processed_content)} bytes')
        print('service + socket time: ', dt_service)
        print()
        holding_content = {
            'name': Name.to_str(name_nosegver),
            'content': processed_content,
            'time': time.time()
        }
        q.put(holding_content)

    # put content
    seg_cnt = (len(processed_content) + SEGMENT_SIZE - 1) // SEGMENT_SIZE
    timestamp = int(holding_content['time'] * 1000)

    if '/32=metadata' in Name.to_str(name) and seg_no < 1:
        # version discovery packet
        metaname = name_nosegver + \
            Name.normalize('/32=metadata') + \
            [Component.from_version(timestamp)] + \
            [Component.from_segment(0)]
        metadata = name_nosegver+[Component.from_version(timestamp)]
        print(f'<< D: {Name.to_str(metaname)}')
        app.put_data(metaname, Name.to_bytes(metadata), freshness_period=10)
        print(MetaInfo(freshness_period=10, final_block_id=0))
        print(f'Content: {len(metadata)} bytes')
        print()
    elif seg_no < seg_cnt:
        # content packet
        putting_name = name_nosegver + \
            [Component.from_version(timestamp)] + \
            [Component.from_segment(seg_no)]
        putting_data = processed_content[seg_no *
                                         SEGMENT_SIZE:(seg_no+1)*SEGMENT_SIZE]
        print(f'<< D: {Name.to_str(putting_name)}')
        app.put_data(putting_name,
                     putting_data,
                     freshness_period=100,
                     final_block_id=Component.from_segment(seg_cnt-1))
        print(MetaInfo(freshness_period=100,
                       final_block_id=seg_cnt-1))
        print(f'Content: {len(putting_data)} bytes')
        print()


if __name__ == '__main__':
    app.run_forever()
