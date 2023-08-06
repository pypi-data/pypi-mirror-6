API capakey service
===================

/capakey: basic endpoint
/capakey/gemeenten: list_gemeenten
/capakey/gemeenten/44001: get_gemeente_by_id
/capakey/gemeenten/44001/afdelingen: list_kadastrale_afdelingen_by_gemeente
/capakey/afdelingen: list_kadastrale_afdelingen
/capakey/afdelingen/44021: get_kadastrale_afdeling_by_id
/capakey/afdelingen/44021/secties: list_secties_by_afdeling
/capakey/afdelingen/44021/secties/A: get_sectie_by_id_and_afdeling
/capakey/afdelingen/44021/secties/A/percelen: list_percelen_by_sectie
/capakey/afdelingen/44021/secties/A/percelen/0452: get_perceel_by_id_and_sectie
/capakey/percelen/44021A3675/00A000: get_perceel_by_capakey
/capakey/percelen/44021_A_blabla: get_perceel_by_percid


* Return format is same as dojo rest store
* Uses Range header for slicing (eg. items=1-10)
* Mime-type is application/json

* Implementation with class based views: CapakeyView
